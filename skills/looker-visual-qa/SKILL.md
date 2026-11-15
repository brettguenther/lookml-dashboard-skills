---
name: looker-visual-qa
description: Renders Looker dashboards (LookML and User-Defined Dashboards across all tabs) and individual Dev-Mode tiles to PNG/PDF via `looker-cli` (`looker_visual_qa.py`), runs deterministic pixel audits, and guides native multimodal visual verification (`read_file`) and surgical self-healing. Use whenever creating, editing, deploying, or auditing Looker dashboards via Looker MCP, `looker-demo-cli`, or standalone LookML files.
---

# Looker Visual QA & Multimodal Inspection (`looker-visual-qa`)

Static YAML linting (`validate_dashboard.py`) and JSON query checks (`run_inline_query json --limit 5`) only prove that SQL compiles (`HTTP 200 OK`)—they **cannot** catch browser/Chromium rendering failures such as blank `modern2026: true` tables, missing column headers, rainbow KPI text, `0%` self-comparisons, axis/legend collisions, 3+ ungrouped Y-axes, `0.0%` null stacked labels, `∅` pie legend slices, or multi-explore cross-filtering warning banners.

Always run this skill's **Render -> Pixel Audit -> Multimodal `read_file` Inspection -> Surgical Self-Heal** loop whenever creating or modifying a Looker dashboard.

---

## 1. Visual Rendering CLI (`looker_visual_qa.py`)

Canonical script path (inside this repository, or invoke via `npx github:brettguenther/lookml-dashboard-skills --visual-qa`):
`scripts/looker_visual_qa.py`

### Mode A: Multi-Tab Full Dashboard Render (Production LookML or UDD)
Automatically discovers all tabs on a LookML dashboard (`model::slug`) or User-Defined Dashboard (`<udd_id>`) and renders every tab concurrently to `1600x1200` PNGs:
```bash
python3 scripts/looker_visual_qa.py render-dashboard \
  --dashboard-id "<model::slug_or_udd_id>" \
  --lookml-path "<optional/path/to/file.dashboard.lookml>" \
  --output-dir "<scratch_dir>/vqa_renders" \
  --json
```
> **Architectural Note (`tab_ids` on LookML vs. UDD)**:
> - For LookML dashboards (`model::slug`), `dashboard_layouts` generates ephemeral UUIDs on every request, so `looker_visual_qa.py` passes `layout["label"]` (e.g., `["Radio & Network Telemetry"]`) in `tab_ids`.
> - For UDDs (`160`), `dashboard_layouts` has persistent database IDs, so `looker_visual_qa.py` passes `str(layout["id"])` (e.g., `["365"]`) in `tab_ids`.

### Mode B: Pre-Production LookML Staging Render (`--stage-udd`)
Looker's headless Chromium renderer (`create_dashboard_render_task`) always renders `model::slug` from **Production** (`workspace_id="production"`). To visually inspect uncommitted multi-tab layout changes from a local `.dashboard.lookml` file *before* merging to production, pass `--stage-udd`:
```bash
python3 scripts/looker_visual_qa.py render-dashboard \
  --lookml-path "<path/to/file.dashboard.lookml>" \
  --stage-udd \
  --output-dir "<scratch_dir>/vqa_staged" \
  --json
```
This imports an ephemeral UDD (`vqa_<hash>`) into the user's personal folder via `looker-cli api dashboard import_dashboard_from_lookml`, renders all tabs concurrently, and automatically deletes the temporary UDD upon completion.

### Mode C: Fast Single-Tile Render (`render-tile`, ~3–8s, Works in Dev Mode!)
When iterating on or fixing a single visualization tile, render just that element using `looker-cli api query run_inline_query png --apply_vis --apply_formatting` (executes in your active session, including Dev Mode):
```bash
python3 scripts/looker_visual_qa.py render-tile \
  --lookml-path "<path/to/file.dashboard.lookml>" \
  --element "<element_name_or_title>" \
  --output "<scratch_dir>/tile_preview.png" \
  --json
```

---

## 2. Mandatory Multimodal `read_file` Inspection Rubric

After running `looker_visual_qa.py`, call your agent's multimodal `read_file` tool on **every PNG path** in `rendered_files` (never skip Tabs 2, 3, or 4!) and verify all 10 visual quality gates:

| # | Visual Check | What to Look For in `read_file` Image | Exact LookML / UDD Remediation |
| :--- | :--- | :--- | :--- |
| **1** | **Table Body & Headers** | Blank white area below table title (`0px` row height) or missing column header row | On `looker_grid` with `modern2026: true`, set integer pixel font sizes (`header_font_size: 12`, `rows_font_size: 12`, **never** `"small"`), `show_view_names: false`, and `show_column_names: true`. |
| **2** | **Table Auto-Cell Bars** | Unwanted horizontal progress bars on the first measure, ID, or rank column | Set `series_cell_visualizations: { <first_measure>: { is_active: false } }`. |
| **3** | **KPI Card Color & Deltas** | Rainbow KPI text (`#6366f1`, `#38bdf8`, `#10b981`, `#f59e0b`), `0%` comparison, or `10000% of X%` | Keep primary KPI text neutral (`#111827` or omit `custom_color`), reserve semantic green/red/amber for comparison deltas, sort time dimension `desc` with `limit: 2`, and omit `comparison_row: first`. |
| **4** | **Custom HTML KPIs** | Overlapping/clipped multiline text or raw unformatted floats (`148.1239481`) | Set `line-height: 1.4; letter-spacing: normal;` on custom HTML wrappers and include all Liquid-referenced measures in `fields: [...]`. |
| **5** | **Legend & X-Axis Overlap** | Bottom legend colliding with X-axis title, or truncated `...` category labels | Remove fixed `"chart": {"marginBottom": ...}` when using bottom legends, or use `legend_position: center`; set `x_axis_label_rotation: -45` or switch to horizontal `looker_bar`. |
| **6** | **Y-Axis Proliferation** | 3+ vertical Y-axes compressing the chart canvas | Explicitly define `y_axes:` with at most 2 axes (`left` and `right`) and bind compatible measures via `series: [{id: field_a}, {id: field_b}]`. |
| **7** | **Stacked Bar `0.0%` Labels** | `0.0%` data labels rendered on empty/null segments of 100% stacked bars | Add `plotOptions.series.dataLabels.filter` (`property: "percentage", operator: ">", value: 0`) in `advanced_vis_config`. |
| **8** | **Null (`∅`) Legend Slices** | Donut/pie or stacked chart legend showing `∅ 0.00%` or `null` | Add `<dimension>: "-NULL"` to the element's `filters:` block. |
| **9** | **Cross-Filter Warning** | Top banner reading `"Unable to cross-filter. Tiles from multiple explores..."` | Set `crossfilter_enabled: false` at the dashboard root whenever tiles span 2+ `(model, explore)` pairs. |
| **10** | **Grid Geometry & Empty Tiles** | Uneven tile heights across a row, dead whitespace holes, or `"No results"` | Align `height` across all tiles sharing a `row`, ensure widths sum to `24` (or `72` in granular mode), and relax overly narrow tile filters. |

---

## 3. Delegating to the `lookml-visual-qa` Subagent

To keep the main conversation context clean during multi-tab rendering and iterative self-healing, delegate Visual QA to the `lookml-visual-qa` subagent via `invoke_subagent`:
- Pass the `--dashboard-id` and/or `--lookml-path`, plus the conversation's artifact `scratch/` directory path so you can optionally embed the final certified tab PNGs into a user-facing markdown carousel.
