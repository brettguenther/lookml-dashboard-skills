#!/usr/bin/env python3
"""Looker Visual QA Engine (`looker_visual_qa.py`).

Deterministic multi-tab dashboard and single-tile PNG/PDF rendering + pixel
sanity checker powered by `looker-cli`. Designed for zero-overhead multimodal
inspection via multimodal agent `read_file` across Looker MCP, `looker-demo-cli`, and
standalone LookML dashboard workflows.

Subcommands:
  1. `render-dashboard`: Renders all tabs of a LookML dashboard (`model::slug`)
     or User-Defined Dashboard (UDD ID) concurrently to high-res PNGs (or PDF),
     with optional pre-production staging UDD import (`--stage-udd`) and static
     AST pre-check (`validate_dashboard.py`).
  2. `render-tile`: Renders a single dashboard element (from a local
     `.dashboard.lookml` file or live dashboard) to PNG in ~3-8s using
     `looker-cli api query run_inline_query png --apply_vis` (supports Dev Mode)
     or `create_dashboard_element_render_task`.
  3. `pixel-audit`: Runs deterministic image dimension, blank-band, and
     whitespace heuristics on rendered PNG files.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from typing import Any

import yaml

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Non-vis_config keys on a LookML dashboard element in `.dashboard.lookml`
_LOOKML_ELEMENT_NON_VIS_KEYS: frozenset[str] = frozenset(
    {
        "name",
        "title",
        "subtitle_text",
        "tab_name",
        "group",
        "model",
        "explore",
        "view",
        "fields",
        "pivots",
        "fill_fields",
        "filters",
        "filter_expression",
        "sorts",
        "limit",
        "column_limit",
        "total",
        "row_total",
        "subtotals",
        "dynamic_fields",
        "query_timezone",
        "listen",
        "row",
        "col",
        "width",
        "height",
        "note_text",
        "note_display",
        "note_state",
        "refresh",
        "auto_run",
        "merged_queries",
        "vis_config",
    }
)


@dataclass
class PixelAuditResult:
    file_path: str
    exists: bool
    size_bytes: int = 0
    width: int = 0
    height: int = 0
    non_bg_ratio: float | None = None
    max_blank_band_px: int = 0
    status: str = "PASS"  # PASS | WARN | FAIL
    findings: list[str] = field(default_factory=list)


@dataclass
class TabRenderResult:
    tab_index: int
    tab_label: str
    tab_identifier: str | None
    render_task_id: str | None
    status: str  # SUCCESS | FAILED
    output_path: str | None = None
    elapsed_seconds: float = 0.0
    error: str | None = None
    pixel_audit: PixelAuditResult | None = None


def find_looker_cli() -> str:
    """Locate the `looker-cli` binary."""
    found = (
        shutil.which("looker-cli")
        or (
            str(Path.home() / ".local" / "bin" / "looker-cli")
            if (Path.home() / ".local" / "bin" / "looker-cli").exists()
            else None
        )
        or (
            str(Path.home() / "bin" / "looker-cli")
            if (Path.home() / "bin" / "looker-cli").exists()
            else None
        )
    )
    if not found:
        raise RuntimeError(
            "`looker-cli` binary not found in PATH or ~/.local/bin/looker-cli."
        )
    return found


def run_looker_cli_json(
    args: list[str],
    body: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    """Execute a `looker-cli` command returning parsed JSON."""
    cli = find_looker_cli()
    cmd = [cli, *args]
    stdin_str = json.dumps(body) if body is not None else None
    if body is not None and "-" not in cmd:
        cmd.append("-")

    res = subprocess.run(
        cmd,
        input=stdin_str,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    out = (res.stdout or "").strip()
    err = (res.stderr or "").strip()
    if res.returncode != 0 or out.startswith("API returned error"):
        raise RuntimeError(
            f"looker-cli {' '.join(args)} failed (rc={res.returncode}): {out or err}"
        )
    if not out:
        return None
    return json.loads(out)


def run_looker_cli_binary(
    args: list[str],
    output_path: Path,
    body: dict[str, Any] | None = None,
    timeout: int = 120,
) -> int:
    """Execute a `looker-cli` command that streams binary bytes to `output_path`."""
    cli = find_looker_cli()
    cmd = [cli, *args]
    stdin_bytes = json.dumps(body).encode("utf-8") if body is not None else None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        res = subprocess.run(
            cmd,
            input=stdin_bytes,
            stdout=f,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    size = output_path.stat().st_size if output_path.exists() else 0
    if res.returncode != 0 or size == 0:
        err_msg = (res.stderr or b"").decode("utf-8", errors="replace").strip()
        # Check if an error text was written to output_path
        head_text = ""
        if output_path.exists() and size < 2048:
            raw = output_path.read_bytes()
            if not raw.startswith((b"\x89PNG", b"%PDF", b"\xff\xd8")):
                head_text = raw.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Binary looker-cli {' '.join(args)} failed (rc={res.returncode}, size={size}): {head_text or err_msg}"
        )
    # Also guard against Looker CLI writing "API returned error ..." as plain text with exit code 0
    if size < 2048:
        raw = output_path.read_bytes()
        if raw.startswith(b"API returned error"):
            raise RuntimeError(raw.decode("utf-8", errors="replace").strip())
    return size


def sanitize_slug(text: str) -> str:
    """Sanitize a tab or element title for filenames."""
    cleaned = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", cleaned) or "untitled"


def parse_png_dimensions(path: Path) -> tuple[int, int]:
    """Read PNG width and height directly from the IHDR chunk."""
    with open(path, "rb") as f:
        header = f.read(24)
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR":
        width, height = struct.unpack(">II", header[16:24])
        return int(width), int(height)
    return 0, 0


def audit_rendered_image(path: Path, is_full_tab: bool = True) -> PixelAuditResult:
    """Perform deterministic pixel and dimension checks on a rendered PNG/PDF."""
    if not path.exists():
        return PixelAuditResult(
            file_path=str(path),
            exists=False,
            status="FAIL",
            findings=["Rendered output file does not exist."],
        )

    size = path.stat().st_size
    if path.suffix.lower() == ".pdf":
        raw_head = path.read_bytes()[:8]
        if not raw_head.startswith(b"%PDF") or size < 1024:
            return PixelAuditResult(
                file_path=str(path),
                exists=True,
                size_bytes=size,
                status="FAIL",
                findings=["Invalid or empty PDF file header."],
            )
        return PixelAuditResult(
            file_path=str(path),
            exists=True,
            size_bytes=size,
            status="PASS",
        )

    width, height = parse_png_dimensions(path)
    result = PixelAuditResult(
        file_path=str(path),
        exists=True,
        size_bytes=size,
        width=width,
        height=height,
    )

    if width == 0 or height == 0 or size < 512:
        result.status = "FAIL"
        result.findings.append(
            f"Corrupt or near-empty PNG ({size} bytes, {width}x{height}px)."
        )
        return result

    if is_full_tab and height < 350:
        result.status = "WARN"
        result.findings.append(
            f"Rendered tab height is unusually short ({height}px) — possible empty tab or collapsed layout."
        )

    if HAS_PIL:
        try:
            with Image.open(path) as img:
                rgb = img.convert("RGB")
                w, h = rgb.size
                # Downsample horizontally by 4x for fast scanline analysis
                small = rgb.resize((max(1, w // 4), h))
                sw, sh = small.size
                pixels = list(
                    small.get_flattened_data()
                    if hasattr(small, "get_flattened_data")
                    else small.getdata()
                )
                # Estimate background color from top-left corner pixel
                bg_r, bg_g, bg_b = pixels[0]

                non_bg_count = 0
                blank_run = 0
                max_blank_run = 0
                # Analyze interior vertical scanlines (skip top 90px header and bottom 50px footer)
                top_skip = min(90, sh // 6)
                bot_skip = max(top_skip + 1, sh - min(50, sh // 10))

                for y in range(sh):
                    row_offset = y * sw
                    row_non_bg = 0
                    for x in range(sw):
                        r, g, b = pixels[row_offset + x]
                        if abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b) > 24:
                            row_non_bg += 1
                    non_bg_count += row_non_bg
                    if top_skip <= y < bot_skip:
                        # Consider scanline "blank" if < 1.5% of pixels differ from background
                        # (accounts for thin left/right card border lines)
                        if (row_non_bg / sw) < 0.015:
                            blank_run += 1
                            if blank_run > max_blank_run:
                                max_blank_run = blank_run
                        else:
                            blank_run = 0

                total_px = max(1, sw * sh)
                result.non_bg_ratio = round(non_bg_count / total_px, 4)
                result.max_blank_band_px = max_blank_run

                if result.non_bg_ratio < 0.02:
                    result.status = "FAIL"
                    result.findings.append(
                        f"Image is >98% uniform background (non_bg_ratio={result.non_bg_ratio:.3f})."
                    )
                elif is_full_tab and max_blank_run >= 260:
                    result.status = "WARN"
                    result.findings.append(
                        f"Detected a {max_blank_run}px tall blank interior horizontal band — "
                        "check for blank `looker_grid` tables (`modern2026: true` with string font sizes), "
                        "'No results' tiles, or uneven grid row heights."
                    )
        except Exception as exc:
            result.findings.append(f"Pillow pixel analysis skipped: {exc}")
    else:
        bytes_per_px = size / max(1, width * height)
        if bytes_per_px < 0.006:
            result.status = "FAIL"
            result.findings.append(
                f"Image has near-zero visual entropy (bytes_per_pixel={bytes_per_px:.4f}) — likely uniform blank background."
            )

    return result


def load_lookml_dashboard_doc(lookml_path: Path) -> dict[str, Any]:
    """Load the primary dashboard document from a `.dashboard.lookml` file."""
    raw = lookml_path.read_text(encoding="utf-8")
    docs = list(yaml.safe_load_all(raw))
    for doc in docs:
        if isinstance(doc, list):
            for item in doc:
                if isinstance(item, dict) and "dashboard" in item:
                    return item
        elif isinstance(doc, dict) and "dashboard" in doc:
            return doc
    raise ValueError(f"No `dashboard:` root key found in {lookml_path}")


def stage_ephemeral_udd_from_lookml(
    lookml_path: Path,
    folder_id: str | None = None,
) -> tuple[str, str]:
    """Import a local `.dashboard.lookml` file as a temporary UDD in the user's personal folder.

    Returns:
        Tuple of (udd_id, preferred_slug).
    """
    if not folder_id:
        me = run_looker_cli_json(["api", "user", "me"])
        folder_id = str((me or {}).get("personal_folder_id") or "1")

    raw_text = lookml_path.read_text(encoding="utf-8")
    doc = load_lookml_dashboard_doc(lookml_path)
    orig_slug = str(doc.get("dashboard") or lookml_path.stem.replace(".dashboard", ""))
    short_hash = hashlib.sha1(orig_slug.encode("utf-8")).hexdigest()[:8]
    staging_slug = f"vqa_{short_hash}"

    # Prepare UDD-compatible LookML YAML (`dashboard:` + `preferred_slug:`, no `slug:`)
    patched_doc = dict(doc)
    patched_doc.pop("slug", None)
    patched_doc["dashboard"] = staging_slug
    patched_doc["preferred_slug"] = staging_slug
    patched_doc["title"] = f"[VQA Staging] {doc.get('title') or orig_slug}"

    yaml_str = yaml.safe_dump([patched_doc], sort_keys=False, allow_unicode=True)
    resp = run_looker_cli_json(
        ["api", "dashboard", "import_dashboard_from_lookml", "-"],
        body={"folder_id": str(folder_id), "lookml": yaml_str},
    )
    if not isinstance(resp, dict) or not resp.get("id"):
        raise RuntimeError(
            f"Failed to stage UDD from {lookml_path} via import_dashboard_from_lookml: {resp}"
        )
    return str(resp["id"]), staging_slug


def delete_staged_udd(udd_id: str) -> None:
    """Delete a temporary staged UDD."""
    try:
        run_looker_cli_json(["api", "dashboard", "delete_dashboard", str(udd_id)])
    except Exception:
        pass


def discover_dashboard_tabs(
    dashboard_id: str,
    lookml_path: Path | None = None,
) -> tuple[str, list[tuple[int, str, str | None]]]:
    """Discover tabs for a LookML dashboard (`model::slug`) or UDD (`123`).

    CRITICAL Looker RenderTask Rule:
    - LookML Dashboards (`"::" in dashboard_id`): `dashboard_layouts` generates
      ephemeral UUIDs per request, so `tab_ids` in `create_dashboard_render_task`
      MUST pass the tab's `label` (or `lookml_link_id` / YAML `tabs:` `name`).
    - User-Defined Dashboards (`"::" not in dashboard_id`): `dashboard_layouts`
      has persistent database IDs, so `tab_ids` MUST pass `str(layout["id"])`.

    Returns:
        Tuple of (dashboard_title, list of (tab_index, tab_label, tab_id_for_rendertask)).
    """
    is_lookml = "::" in str(dashboard_id)
    title = str(dashboard_id)
    tabs: list[tuple[int, str, str | None]] = []

    try:
        dash_meta = run_looker_cli_json(
            ["api", "dashboard", "dashboard", str(dashboard_id)]
        )
    except Exception as exc:
        dash_meta = None
        if lookml_path and lookml_path.exists() and is_lookml:
            doc = load_lookml_dashboard_doc(lookml_path)
            title = str(doc.get("title") or dashboard_id)
            yaml_tabs = doc.get("tabs") or []
            if isinstance(yaml_tabs, list) and yaml_tabs:
                for idx, t in enumerate(yaml_tabs):
                    if isinstance(t, dict):
                        t_label = str(t.get("label") or t.get("name") or f"Tab {idx + 1}")
                        t_name = str(t.get("name") or t_label)
                        tabs.append((idx, t_label, t_name))
                return title, tabs
        raise RuntimeError(
            f"Could not fetch dashboard `{dashboard_id}` via looker-cli: {exc}"
        ) from exc

    if isinstance(dash_meta, dict):
        title = str(dash_meta.get("title") or dashboard_id)
        layouts = [
            lay
            for lay in (dash_meta.get("dashboard_layouts") or [])
            if isinstance(lay, dict) and not lay.get("deleted")
        ]
        layouts.sort(key=lambda x: (x.get("order") is None, x.get("order") or 0))
        if len(layouts) <= 1:
            lay_label = (
                str(layouts[0].get("label") or "Main")
                if layouts and layouts[0].get("label")
                else "Main"
            )
            # Single-tab dashboard: no tab_ids filter needed
            tabs.append((0, lay_label, None))
        else:
            for idx, lay in enumerate(layouts):
                label = str(
                    lay.get("label")
                    or lay.get("lookml_link_id")
                    or f"Tab {idx + 1}"
                )
                if is_lookml:
                    # LookML dashboard requires tab label / lookml_link_id
                    tab_identifier = str(lay.get("label") or lay.get("lookml_link_id"))
                else:
                    # UDD requires persistent numeric/string layout ID
                    tab_identifier = str(lay.get("id"))
                tabs.append((idx, label, tab_identifier))

    if not tabs:
        tabs.append((0, "Main", None))
    return title, tabs


def _render_single_tab_worker(
    dashboard_id: str,
    tab_index: int,
    tab_label: str,
    tab_identifier: str | None,
    output_dir: Path,
    result_format: str = "png",
    width: int = 1600,
    height: int = 1200,
    theme: str | None = None,
    dashboard_filters: str | None = None,
    pdf_landscape: bool = True,
    timeout: int = 120,
) -> TabRenderResult:
    """Create, poll, and download a RenderTask for a single dashboard tab."""
    t0 = time.time()
    slug = sanitize_slug(tab_label)
    ext = result_format.lower()
    out_file = output_dir / f"tab_{tab_index + 1:02d}_{slug}.{ext}"

    body: dict[str, Any] = {"dashboard_style": "tiled"}
    if tab_identifier is not None:
        body["tab_ids"] = [tab_identifier]
    if dashboard_filters:
        body["dashboard_filters"] = dashboard_filters

    cmd = [
        "api",
        "rendertask",
        "create_dashboard_render_task",
        str(dashboard_id),
        ext,
        str(width),
        str(height),
        "-",
    ]
    if theme:
        cmd.extend(["--theme", theme])
    if ext == "pdf" and pdf_landscape:
        cmd.append("--pdf_landscape")

    try:
        task_obj = run_looker_cli_json(cmd, body=body, timeout=30)
        task_id = str((task_obj or {}).get("id") or "")
        if not task_id:
            return TabRenderResult(
                tab_index=tab_index,
                tab_label=tab_label,
                tab_identifier=tab_identifier,
                render_task_id=None,
                status="FAILED",
                elapsed_seconds=round(time.time() - t0, 2),
                error=f"No render_task id returned: {task_obj}",
            )

        deadline = time.time() + timeout
        last_status = "created"
        status_detail = ""
        while time.time() < deadline:
            time.sleep(2.0)
            st = run_looker_cli_json(
                ["api", "rendertask", "render_task", task_id], timeout=30
            )
            if not isinstance(st, dict):
                continue
            last_status = str(st.get("status") or "")
            status_detail = str(st.get("status_detail") or "")
            if last_status == "success":
                break
            if last_status in ("failure", "error"):
                return TabRenderResult(
                    tab_index=tab_index,
                    tab_label=tab_label,
                    tab_identifier=tab_identifier,
                    render_task_id=task_id,
                    status="FAILED",
                    elapsed_seconds=round(time.time() - t0, 2),
                    error=f"RenderTask {task_id} ended with status={last_status}: {status_detail}",
                )
        else:
            return TabRenderResult(
                tab_index=tab_index,
                tab_label=tab_label,
                tab_identifier=tab_identifier,
                render_task_id=task_id,
                status="FAILED",
                elapsed_seconds=round(time.time() - t0, 2),
                error=f"RenderTask {task_id} timed out after {timeout}s (last_status={last_status})",
            )

        run_looker_cli_binary(
            ["api", "rendertask", "render_task_results", task_id],
            output_path=out_file,
            timeout=60,
        )
        audit = audit_rendered_image(out_file, is_full_tab=True)
        return TabRenderResult(
            tab_index=tab_index,
            tab_label=tab_label,
            tab_identifier=tab_identifier,
            render_task_id=task_id,
            status="SUCCESS",
            output_path=str(out_file.resolve()),
            elapsed_seconds=round(time.time() - t0, 2),
            pixel_audit=audit,
        )
    except Exception as exc:
        return TabRenderResult(
            tab_index=tab_index,
            tab_label=tab_label,
            tab_identifier=tab_identifier,
            render_task_id=None,
            status="FAILED",
            elapsed_seconds=round(time.time() - t0, 2),
            error=str(exc),
        )


def convert_lookml_element_to_write_query(
    element: dict[str, Any],
    default_model: str | None = None,
) -> dict[str, Any]:
    """Convert a `.dashboard.lookml` element dictionary into a Looker `WriteQuery` JSON body."""
    model = str(element.get("model") or default_model or "")
    view = str(element.get("explore") or element.get("view") or "")
    if not model or not view:
        raise ValueError(
            f"Element `{element.get('name') or element.get('title')}` is missing `model` or `explore`."
        )

    vis_config: dict[str, Any] = {}
    if isinstance(element.get("vis_config"), dict):
        vis_config.update(element["vis_config"])
    for k, v in element.items():
        if k not in _LOOKML_ELEMENT_NON_VIS_KEYS and v is not None:
            vis_config[k] = v
    if element.get("type") and "type" not in vis_config:
        vis_config["type"] = element["type"]

    sorts = element.get("sorts")
    if isinstance(sorts, str):
        sorts = [sorts]

    dyn_fields = element.get("dynamic_fields")
    if isinstance(dyn_fields, list):
        dyn_fields = json.dumps(dyn_fields)

    body: dict[str, Any] = {
        "model": model,
        "view": view,
        "fields": element.get("fields") or [],
        "pivots": element.get("pivots"),
        "fill_fields": element.get("fill_fields"),
        "filters": element.get("filters"),
        "filter_expression": element.get("filter_expression"),
        "sorts": sorts,
        "limit": str(element.get("limit") or "500"),
        "column_limit": (
            str(element["column_limit"])
            if element.get("column_limit") is not None
            else None
        ),
        "total": element.get("total"),
        "row_total": element.get("row_total"),
        "subtotals": element.get("subtotals"),
        "dynamic_fields": dyn_fields,
        "query_timezone": element.get("query_timezone"),
        "vis_config": vis_config,
    }
    return {k: v for k, v in body.items() if v is not None}


def render_single_tile(
    output_path: Path,
    lookml_path: Path | None = None,
    dashboard_id: str | None = None,
    element_target: str | None = None,
    default_model: str | None = None,
    width: int = 800,
    height: int = 500,
    timeout: int = 60,
) -> dict[str, Any]:
    """Render a single tile to PNG via `looker-cli api query run_inline_query png` (works in Dev Mode!)."""
    t0 = time.time()
    query_body: dict[str, Any] | None = None
    matched_title = element_target or "tile"

    if lookml_path and lookml_path.exists():
        doc = load_lookml_dashboard_doc(lookml_path)
        elements = doc.get("elements") or []
        target_lower = (element_target or "").strip().lower()
        chosen = None
        for el in elements:
            if not isinstance(el, dict):
                continue
            if el.get("type") in ("text", "group") and not el.get("fields"):
                continue
            name_val = str(el.get("name") or "").lower()
            title_val = str(el.get("title") or "").lower()
            if not target_lower or target_lower in (name_val, title_val) or target_lower in title_val or target_lower in name_val:
                chosen = el
                break
        if not chosen:
            raise ValueError(
                f"Element `{element_target}` not found in {lookml_path}."
            )
        matched_title = str(chosen.get("title") or chosen.get("name") or "tile")
        query_body = convert_lookml_element_to_write_query(
            chosen, default_model=default_model or doc.get("model")
        )
    elif dashboard_id:
        dash_meta = run_looker_cli_json(
            ["api", "dashboard", "dashboard", str(dashboard_id)]
        )
        elems = (dash_meta or {}).get("dashboard_elements") or []
        target_lower = (element_target or "").strip().lower()
        chosen_elem = None
        for el in elems:
            if not isinstance(el, dict):
                continue
            q = el.get("query") or (el.get("result_maker") or {}).get("query")
            if not q:
                continue
            el_id = str(el.get("id") or "").lower()
            el_title = str(el.get("title") or "").lower()
            if not target_lower or target_lower in (el_id, el_title) or target_lower in el_title:
                chosen_elem = el
                break
        if not chosen_elem:
            raise ValueError(
                f"Query element `{element_target}` not found on dashboard `{dashboard_id}`."
            )
        matched_title = str(chosen_elem.get("title") or chosen_elem.get("id"))
        q = chosen_elem.get("query") or chosen_elem["result_maker"]["query"]
        query_body = {
            "model": q["model"],
            "view": q["view"],
            "fields": q.get("fields") or [],
            "pivots": q.get("pivots"),
            "fill_fields": q.get("fill_fields"),
            "filters": q.get("filters"),
            "filter_expression": q.get("filter_expression"),
            "sorts": q.get("sorts"),
            "limit": str(q.get("limit") or "500"),
            "column_limit": q.get("column_limit"),
            "total": q.get("total"),
            "row_total": q.get("row_total"),
            "subtotals": q.get("subtotals"),
            "dynamic_fields": q.get("dynamic_fields"),
            "vis_config": q.get("vis_config"),
        }
        query_body = {k: v for k, v in query_body.items() if v is not None}
    else:
        raise ValueError("Provide either --lookml-path or --dashboard-id.")

    run_looker_cli_binary(
        [
            "api",
            "query",
            "run_inline_query",
            "png",
            "-",
            "--apply_vis",
            "--apply_formatting",
            "--image_width",
            str(width),
            "--image_height",
            str(height),
        ],
        output_path=output_path,
        body=query_body,
        timeout=timeout,
    )
    elapsed = round(time.time() - t0, 2)
    audit = audit_rendered_image(output_path, is_full_tab=False)
    return {
        "status": "SUCCESS" if audit.status != "FAIL" else "FAILED",
        "element_title": matched_title,
        "output_path": str(output_path.resolve()),
        "elapsed_seconds": elapsed,
        "pixel_audit": asdict(audit),
    }


def run_static_validator(lookml_path: Path) -> dict[str, Any]:
    """Run `validate_dashboard.py` on a `.dashboard.lookml` file if present."""
    validator_script = Path(__file__).resolve().parent / "validate_dashboard.py"
    if not validator_script.exists():
        return {"ran": False, "passed": True, "output": "validate_dashboard.py not found"}
    res = subprocess.run(
        [sys.executable, str(validator_script), str(lookml_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "ran": True,
        "passed": res.returncode == 0,
        "returncode": res.returncode,
        "output": (res.stdout + "\n" + res.stderr).strip(),
    }


def render_dashboard_workflow(
    dashboard_id: str | None = None,
    lookml_path: Path | None = None,
    model: str | None = None,
    stage_udd: bool = False,
    keep_staged_udd: bool = False,
    tab_filter: list[str] | None = None,
    theme: str | None = None,
    dashboard_filters: str | None = None,
    result_format: str = "png",
    width: int = 1600,
    height: int = 1200,
    output_dir: Path = Path("./vqa_renders"),
    max_workers: int = 3,
    timeout: int = 120,
    skip_static: bool = False,
) -> dict[str, Any]:
    """Execute end-to-end multi-tab dashboard rendering and pixel audit."""
    static_report: dict[str, Any] = {"ran": False, "passed": True}
    if lookml_path and lookml_path.exists() and not skip_static:
        static_report = run_static_validator(lookml_path)

    staged_udd_id: str | None = None
    target_dashboard_id = dashboard_id

    if stage_udd:
        if not lookml_path or not lookml_path.exists():
            raise ValueError("--stage-udd requires a valid --lookml-path.")
        staged_udd_id, _ = stage_ephemeral_udd_from_lookml(lookml_path)
        target_dashboard_id = staged_udd_id
    elif not target_dashboard_id and lookml_path and lookml_path.exists():
        doc = load_lookml_dashboard_doc(lookml_path)
        slug = str(doc.get("dashboard") or lookml_path.stem.replace(".dashboard", ""))
        resolved_model = model or doc.get("model")
        if not resolved_model:
            for el in doc.get("elements") or []:
                if isinstance(el, dict) and el.get("model"):
                    resolved_model = str(el["model"])
                    break
        if not resolved_model:
            raise ValueError(
                "Could not infer LookML `model` from `.dashboard.lookml`; pass `--model <model>` or `--dashboard-id <id>`."
            )
        target_dashboard_id = f"{resolved_model}::{slug}"

    if not target_dashboard_id:
        raise ValueError("Provide `--dashboard-id` or `--lookml-path`.")

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        dash_title, tabs = discover_dashboard_tabs(
            target_dashboard_id, lookml_path=lookml_path
        )
        if tab_filter:
            wanted = {t.strip().lower() for t in tab_filter if t.strip()}
            tabs = [
                (idx, lbl, tid)
                for idx, lbl, tid in tabs
                if lbl.lower() in wanted
                or (tid and tid.lower() in wanted)
                or str(idx + 1) in wanted
                or any(w in lbl.lower() for w in wanted)
            ]
            if not tabs:
                raise ValueError(
                    f"No tabs on `{target_dashboard_id}` matched filter {tab_filter}."
                )

        tab_results: list[TabRenderResult] = []
        with ThreadPoolExecutor(max_workers=max(1, min(max_workers, len(tabs)))) as pool:
            futures = {
                pool.submit(
                    _render_single_tab_worker,
                    dashboard_id=target_dashboard_id,
                    tab_index=idx,
                    tab_label=lbl,
                    tab_identifier=tid,
                    output_dir=output_dir,
                    result_format=result_format,
                    width=width,
                    height=height,
                    theme=theme,
                    dashboard_filters=dashboard_filters,
                    timeout=timeout,
                ): (idx, lbl)
                for idx, lbl, tid in tabs
            }
            for fut in as_completed(futures):
                tab_results.append(fut.result())

        tab_results.sort(key=lambda r: r.tab_index)
    finally:
        if staged_udd_id and not keep_staged_udd:
            delete_staged_udd(staged_udd_id)

    all_rendered_ok = all(r.status == "SUCCESS" for r in tab_results)
    any_pixel_fail = any(
        (r.pixel_audit and r.pixel_audit.status == "FAIL") for r in tab_results
    )
    overall_status = (
        "SUCCESS"
        if (all_rendered_ok and not any_pixel_fail and static_report.get("passed", True))
        else "WARN_OR_FAIL"
    )

    rendered_files = [r.output_path for r in tab_results if r.output_path]
    return {
        "status": overall_status,
        "dashboard_id": target_dashboard_id,
        "dashboard_title": dash_title,
        "staged_udd_id": staged_udd_id,
        "static_validation": static_report,
        "tabs_count": len(tab_results),
        "rendered_files": rendered_files,
        "tabs": [asdict(r) for r in tab_results],
        "agent_next_step": (
            "Call `read_file` on EVERY image path in `rendered_files` to visually inspect "
            "each tab against the 10-Point Looker Visual QA Rubric (blank modern2026 grids, "
            "unwanted cell bars, 0% PoP KPIs, rainbow KPI colors, custom HTML truncation, "
            "axis/legend overlaps, 3+ ungrouped Y-axes, 0.0% null stacked bar labels, "
            "multi-explore crossfilter warning banners, and dead grid whitespace)."
        ),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="looker_visual_qa.py",
        description="Looker Visual QA Engine (multi-tab RenderTask & Dev-Mode inline tile renderer).",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # 1. render-dashboard
    p_dash = sub.add_parser(
        "render-dashboard",
        help="Render all tabs of a LookML dashboard or UDD to PNG/PDF and run pixel audit.",
    )
    p_dash.add_argument(
        "--dashboard-id",
        help="LookML dashboard ID (`model::slug`) or UDD ID (`123`).",
    )
    p_dash.add_argument(
        "--lookml-path",
        type=Path,
        help="Path to local `.dashboard.lookml` file.",
    )
    p_dash.add_argument(
        "--model",
        help="LookML model name (when deriving `model::slug` from `--lookml-path`).",
    )
    p_dash.add_argument(
        "--stage-udd",
        action="store_true",
        help="Import `--lookml-path` as an ephemeral staging UDD in personal folder before rendering (renders uncommitted layout changes without prod deploy).",
    )
    p_dash.add_argument(
        "--keep-staged-udd",
        action="store_true",
        help="Do not delete the ephemeral staged UDD after rendering.",
    )
    p_dash.add_argument(
        "--tab",
        action="append",
        default=[],
        help="Render only specific tab name(s), ID(s), or 1-based index (can be repeated).",
    )
    p_dash.add_argument(
        "--theme",
        help="Optional Looker theme name to apply during rendering.",
    )
    p_dash.add_argument(
        "--filters",
        help="Optional URL query string of dashboard filters (e.g. 'Date=30 days').",
    )
    p_dash.add_argument(
        "--format",
        choices=["png", "pdf"],
        default="png",
        help="Render output format (default: png).",
    )
    p_dash.add_argument("--width", type=int, default=1600, help="Viewport width (default: 1600).")
    p_dash.add_argument("--height", type=int, default=1200, help="Viewport height (default: 1200).")
    p_dash.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./vqa_renders"),
        help="Output directory for rendered images.",
    )
    p_dash.add_argument("--max-workers", type=int, default=3, help="Concurrent tab render workers.")
    p_dash.add_argument("--timeout", type=int, default=120, help="RenderTask timeout in seconds.")
    p_dash.add_argument("--skip-static", action="store_true", help="Skip static YAML validation.")
    p_dash.add_argument("--json", action="store_true", help="Emit JSON output.")

    # 2. render-tile
    p_tile = sub.add_parser(
        "render-tile",
        help="Render a single dashboard element to PNG via `run_inline_query png` (works in Dev Mode).",
    )
    p_tile.add_argument("--lookml-path", type=Path, help="Local `.dashboard.lookml` path.")
    p_tile.add_argument("--dashboard-id", help="Live LookML or UDD dashboard ID.")
    p_tile.add_argument(
        "--element",
        required=True,
        help="Element `name`, `title`, or `id` (substring match supported).",
    )
    p_tile.add_argument("--model", help="Fallback LookML model name.")
    p_tile.add_argument("--width", type=int, default=800, help="Image width (default: 800).")
    p_tile.add_argument("--height", type=int, default=500, help="Image height (default: 500).")
    p_tile.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output `.png` file path.",
    )
    p_tile.add_argument("--timeout", type=int, default=60, help="Timeout in seconds.")
    p_tile.add_argument("--json", action="store_true", help="Emit JSON output.")

    # 3. pixel-audit
    p_audit = sub.add_parser(
        "pixel-audit",
        help="Run deterministic dimension and blank-band checks on rendered PNG/PDF files.",
    )
    p_audit.add_argument("files", nargs="+", type=Path, help="PNG/PDF files to audit.")
    p_audit.add_argument("--json", action="store_true", help="Emit JSON output.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.subcommand == "render-dashboard":
        report = render_dashboard_workflow(
            dashboard_id=args.dashboard_id,
            lookml_path=args.lookml_path,
            model=args.model,
            stage_udd=args.stage_udd,
            keep_staged_udd=args.keep_staged_udd,
            tab_filter=args.tab or None,
            theme=args.theme,
            dashboard_filters=args.filters,
            result_format=args.format,
            width=args.width,
            height=args.height,
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            timeout=args.timeout,
            skip_static=args.skip_static,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"=== Looker Visual QA: {report['dashboard_title']} ({report['dashboard_id']}) ==="
            )
            if report["static_validation"].get("ran"):
                st_ok = report["static_validation"]["passed"]
                print(f"Static YAML Validation: {'PASS' if st_ok else 'FAIL'}")
                if not st_ok:
                    print(report["static_validation"]["output"])
            for t in report["tabs"]:
                pa = t.get("pixel_audit") or {}
                dims = (
                    f"{pa.get('width', 0)}x{pa.get('height', 0)}px, {pa.get('size_bytes', 0):,}B"
                    if pa
                    else ""
                )
                print(
                    f"  [Tab {t['tab_index'] + 1}: {t['tab_label']}] {t['status']} "
                    f"({t['elapsed_seconds']}s) -> {t.get('output_path') or t.get('error')} ({dims})"
                )
                for finding in pa.get("findings") or []:
                    print(f"    ⚠️  {finding}")
            print(f"\nNext Step: {report['agent_next_step']}")
        return 0 if report["status"] == "SUCCESS" else 1

    if args.subcommand == "render-tile":
        report = render_single_tile(
            output_path=args.output,
            lookml_path=args.lookml_path,
            dashboard_id=args.dashboard_id,
            element_target=args.element,
            default_model=args.model,
            width=args.width,
            height=args.height,
            timeout=args.timeout,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            pa = report["pixel_audit"]
            print(
                f"[{report['status']}] Rendered tile '{report['element_title']}' in {report['elapsed_seconds']}s "
                f"-> {report['output_path']} ({pa['width']}x{pa['height']}px, {pa['size_bytes']:,}B)"
            )
            for finding in pa.get("findings") or []:
                print(f"  ⚠️  {finding}")
        return 0 if report["status"] == "SUCCESS" else 1

    if args.subcommand == "pixel-audit":
        results = [asdict(audit_rendered_image(f)) for f in args.files]
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(
                    f"[{r['status']}] {r['file_path']} ({r['width']}x{r['height']}px, {r['size_bytes']:,}B, "
                    f"non_bg={r['non_bg_ratio']}, max_blank_band={r['max_blank_band_px']}px)"
                )
                for f in r["findings"]:
                    print(f"  ⚠️  {f}")
        return 0 if all(r["status"] != "FAIL" for r in results) else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
