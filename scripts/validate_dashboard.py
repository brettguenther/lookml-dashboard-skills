#!/usr/bin/env python3
"""LookML Dashboard Validator

Validates LookML dashboard files (*.dashboard.lookml) against fatal rendering
and compiler constraints.

Omit stylistic constraints — only checks conditions expected to break rendering.
"""

import sys
import os
import argparse
import re
import yaml

MODERN2026_SUPPORTED = {
    'looker_column',
    'looker_bar',
    'looker_line',
    'looker_area',
    'looker_scatter',
    'looker_waterfall',
    'looker_boxplot',
    'looker_histogram',
    'looker_bullet',
    'looker_grid',
    'table',
    'looker_funnel',
    'looker_timeline',
    'looker_wordcloud',
    'looker_pie',
    'looker_donut_multiples',
}

MODERN2026_UNSUPPORTED = {
    'single_value',
    'looker_single_record',
    'single_record',
    'looker_google_map',
    'looker_geo_choropleth',
    'looker_geo_coordinates',
    'text',
    'group',
}

VALID_COMPARISON_ROWS = {'first', 'second', 'last', 'total'}
PREFERRED_SLUG_RE = re.compile(r"^[A-Za-z0-9_-]{10,50}$")
LEGACY_YES_NO_RE = re.compile(
    r"^\s*(modern2026|crossfilter_enabled|show_comparison|comparison_reverse_colors|"
    r"title_hidden|allow_multiple_values|required|show_view_names|show_row_numbers|"
    r"transpose|truncate_text|enable_conditional_formatting|stacking_enabled)\s*:\s*(yes|no)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def validate_dashboard_dict(dash, filepath):
    errors = []
    dash_name = dash.get('dashboard') or dash.get('title') or 'unnamed_dashboard'

    # Check top-level dashboard ID
    dash_id = dash.get('dashboard')
    if not dash_id:
        errors.append(
            f"[{dash_name}] Missing required top-level 'dashboard: <snake_case_id>'. "
            "Looker API POST /api/4.0/dashboards/lookml fails with HTTP 422 'dashboard is required' without it."
        )
    elif '.' in str(dash_id) or ' ' in str(dash_id):
        errors.append(
            f"[{dash_name}] Top-level 'dashboard: {dash_id}' must be snake_case/slug-safe (no spaces or periods)."
        )

    # Check top-level slug vs preferred_slug
    if 'slug' in dash:
        errors.append(
            f"[{dash_name}] Top-level 'slug:' is invalid in LookML dashboards and causes HTTP 422 on import. "
            "Remove 'slug:' and set 'preferred_slug:' instead."
        )
    preferred_slug = dash.get('preferred_slug')
    if preferred_slug and not PREFERRED_SLUG_RE.match(str(preferred_slug)):
        errors.append(
            f"[{dash_name}] Invalid 'preferred_slug: {preferred_slug}'. "
            "Must match ^[A-Za-z0-9_-]{10,50}$ (10 to 50 chars, letters/digits/hyphens/underscores only)."
        )
    
    # 1. Check declared tabs
    declared_tabs = set()
    if 'tabs' in dash and isinstance(dash['tabs'], list):
        for tab in dash['tabs']:
            if isinstance(tab, dict) and 'name' in tab:
                declared_tabs.add(tab['name'])

    # 2. Check filters for fatal period (.) in name and collect declared filter names
    declared_filters = set()
    if 'filters' in dash and isinstance(dash['filters'], list):
        for f in dash['filters']:
            if isinstance(f, dict):
                fname = f.get('name', '')
                if fname:
                    declared_filters.add(str(fname))
                if '.' in str(fname):
                    errors.append(
                        f"[{dash_name}] Filter name '{fname}' contains a period ('.'). "
                        "Looker LookML compiler crashes on periods in filter names."
                    )

    # 3. Check elements
    elements = dash.get('elements', [])
    if not isinstance(elements, list):
        errors.append(f"[{dash_name}] 'elements' must be a list of element objects.")
        return errors

    distinct_explores = set()
    max_cols = 72 if (dash.get('layout_granularity') == 'granular' or dash.get('col_width') == 15) else 24

    for idx, elem in enumerate(elements):
        if not isinstance(elem, dict):
            continue
        ename = elem.get('name') or elem.get('title') or f"element_{idx}"
        etype = elem.get('type')

        if elem.get('model') and elem.get('explore'):
            distinct_explores.add((str(elem['model']), str(elem['explore'])))

        # Check fatal period (.) in element name
        if elem.get('name') and '.' in str(elem['name']):
            errors.append(
                f"[{dash_name} -> {ename}] Element name '{elem['name']}' contains a period ('.'). "
                "Looker LookML compiler crashes on periods in element names."
            )

        # Check grid layout geometry
        for g_key in ('row', 'col', 'width', 'height'):
            g_val = elem.get(g_key)
            if g_val is None or not isinstance(g_val, int) or g_val < 0:
                errors.append(
                    f"[{dash_name} -> {ename}] Missing or invalid '{g_key}: {g_val}'. "
                    "Every element must specify non-negative integer row, col, width, and height."
                )
        col = elem.get('col')
        width = elem.get('width')
        if isinstance(col, int) and isinstance(width, int):
            if width <= 0 or col + width > max_cols:
                errors.append(
                    f"[{dash_name} -> {ename}] Invalid {max_cols}-column geometry: col={col}, width={width} "
                    f"(col + width = {col + width} > {max_cols})."
                )

        # Check tab assignment if dashboard declares tabs
        if declared_tabs:
            tab_name = elem.get('tab_name')
            if not tab_name:
                errors.append(
                    f"[{dash_name} -> {ename}] Missing 'tab_name'. Dashboard defines tabs "
                    f"({', '.join(sorted(declared_tabs))}) but element is not assigned to any tab."
                )
            elif tab_name not in declared_tabs:
                errors.append(
                    f"[{dash_name} -> {ename}] 'tab_name: {tab_name}' does not match any declared tab "
                    f"({', '.join(sorted(declared_tabs))})."
                )

        # Check modern2026: true requirement on supported elements
        if etype in MODERN2026_SUPPORTED:
            if not elem.get('modern2026'):
                errors.append(
                    f"[{dash_name} -> {ename}] Element type '{etype}' must have 'modern2026: true' "
                    "for modern rendering engine compliance."
                )

        # Check modern2026 must be omitted on unsupported elements
        if etype in MODERN2026_UNSUPPORTED or etype == 'text':
            if elem.get('modern2026'):
                errors.append(
                    f"[{dash_name} -> {ename}] Element type '{etype}' does NOT support 'modern2026'. "
                    "Omit 'modern2026: true' to avoid rendering errors."
                )

        # Check looker_grid / table font sizes: string font sizes cause NaN (0px) row height when modern2026: true
        if etype in ('looker_grid', 'table') and elem.get('modern2026'):
            for font_key in ('rows_font_size', 'header_font_size'):
                if font_key in elem and isinstance(elem[font_key], str):
                    errors.append(
                        f"[{dash_name} -> {ename}] '{font_key}: {elem[font_key]}' is a string on a modern2026 {etype}. "
                        "String font sizes cause NaN (0px) row heights and render blank tables. Use a numeric pixel integer (e.g. 12)."
                    )

        # Check single_value comparison configuration (comparison_series & comparison_row)
        if etype == 'single_value' and elem.get('show_comparison'):
            comp_row = elem.get('comparison_row')
            comp_series = elem.get('comparison_series')
            fields_list = elem.get('fields') if isinstance(elem.get('fields'), list) else []
            has_dynamic = bool(elem.get('dynamic_fields'))
            sorts = elem.get('sorts') or []
            limit_val = elem.get('limit')
            is_multi_row_pop = bool(sorts) or (isinstance(limit_val, int) and limit_val > 1)

            if comp_row is not None:
                if not isinstance(comp_row, str) or comp_row not in VALID_COMPARISON_ROWS:
                    errors.append(
                        f"[{dash_name} -> {ename}] Invalid 'comparison_row: {comp_row}'. "
                        f"Must be one of {sorted(VALID_COMPARISON_ROWS)} (use 'second' for Row 1 vs Row 2 PoP)."
                    )
                elif comp_row == 'first' and not has_dynamic:
                    if any('desc' in str(s).lower() for s in sorts):
                        errors.append(
                            f"[{dash_name} -> {ename}] 'comparison_row: first' with descending sort and no dynamic_fields "
                            "compares Row 1 against Row 1 (0% change). Set 'comparison_row: second' for Row 1 vs Row 2 PoP."
                        )
            elif len(fields_list) >= 2 and not has_dynamic and is_multi_row_pop:
                errors.append(
                    f"[{dash_name} -> {ename}] Missing 'comparison_row: second' on multi-row single_value with 'show_comparison: true' "
                    "and multiple fields (no dynamic_fields). Set 'comparison_row: second' to compare Row 1 (current) against Row 2 (prior)."
                )

            if len(fields_list) >= 2 and not has_dynamic and is_multi_row_pop and not comp_series:
                errors.append(
                    f"[{dash_name} -> {ename}] Missing 'comparison_series' on multi-row single_value with 'show_comparison: true' "
                    f"and fields {fields_list}. Explicitly set 'comparison_series: <view.measure>' so Looker compares the metric rather than the timeframe dimension."
                )
            elif comp_series and fields_list and not has_dynamic and str(comp_series) not in [str(f) for f in fields_list]:
                errors.append(
                    f"[{dash_name} -> {ename}] 'comparison_series: {comp_series}' is not present in element 'fields: {fields_list}'."
                )

        # Check y_axes series structure: series MUST be objects with 'id', not plain strings
        if 'y_axes' in elem and isinstance(elem['y_axes'], list):
            for axis_idx, y_axis in enumerate(elem['y_axes']):
                if isinstance(y_axis, dict) and 'series' in y_axis:
                    series_list = y_axis['series']
                    if isinstance(series_list, list):
                        for s_idx, s_entry in enumerate(series_list):
                            if isinstance(s_entry, str):
                                errors.append(
                                    f"[{dash_name} -> {ename}] y_axes[{axis_idx}].series[{s_idx}] is a plain string ('{s_entry}'). "
                                    "It must be an object with an 'id' key (e.g. `{{id: '{s_entry}'}}`). "
                                    "Passing strings causes fatal frontend crash: \"Cannot create property 'id' on string\"."
                                )

        # Check listen filter references against declared filters
        listen = elem.get('listen')
        if isinstance(listen, dict) and declared_filters:
            for filter_ref in listen.keys():
                if str(filter_ref) not in declared_filters:
                    errors.append(
                        f"[{dash_name} -> {ename}] 'listen' references undeclared filter '{filter_ref}' "
                        f"(declared filters: {sorted(declared_filters)})."
                    )

    # 4. Check crossfilter_enabled across multiple explores
    if dash.get('crossfilter_enabled') is True and len(distinct_explores) > 1:
        explore_list = ", ".join(f"{m}.{e}" for m, e in sorted(distinct_explores))
        errors.append(
            f"[{dash_name}] 'crossfilter_enabled: true' is set on a dashboard querying multiple explores ({explore_list}). "
            "This triggers Looker's 'Unable to cross-filter. Tiles from multiple explores have been added to this dashboard' warning banner. "
            "Set 'crossfilter_enabled: false'."
        )

    return errors


def validate_file(filepath):
    all_errors = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            for match in LEGACY_YES_NO_RE.finditer(raw_text):
                key_name, bad_bool = match.group(1), match.group(2)
                replacement = "true" if bad_bool.lower() == "yes" else "false"
                all_errors.append(
                    f"Legacy LookML boolean '{key_name}: {bad_bool}' detected in {filepath}. "
                    f"Use YAML boolean '{key_name}: {replacement}' instead."
                )
            content = yaml.safe_load(raw_text)
    except Exception as e:
        return [f"YAML parse error in {filepath}: {e}"]

    if not content:
        return [f"File {filepath} is empty."]

    dashboards = content if isinstance(content, list) else [content]
    for dash in dashboards:
        if isinstance(dash, dict):
            all_errors.extend(validate_dashboard_dict(dash, filepath))
    return all_errors


def main():
    parser = argparse.ArgumentParser(description="Validate LookML Dashboard for fatal rendering issues.")
    parser.add_argument("paths", nargs="+", help="LookML dashboard file(s) or directories to validate.")
    args = parser.parse_args()

    files_to_check = []
    for p in args.paths:
        if os.path.isfile(p):
            files_to_check.append(p)
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith('.dashboard.lookml') or f.endswith('.dashboard.lkml') or f.endswith('.lookml'):
                        files_to_check.append(os.path.join(root, f))

    if not files_to_check:
        print("No dashboard LookML files found to validate.")
        sys.exit(0)

    total_errors = 0
    for fpath in files_to_check:
        errors = validate_file(fpath)
        if errors:
            total_errors += len(errors)
            print(f"\n❌ FAIL: {fpath} ({len(errors)} error{'s' if len(errors) > 1 else ''})")
            for err in errors:
                print(f"   • {err}")
        else:
            print(f"✅ PASS: {fpath}")

    if total_errors > 0:
        print(f"\nValidation failed with {total_errors} total rendering error(s).")
        sys.exit(1)
    else:
        print(f"\nAll {len(files_to_check)} dashboard file(s) passed validation.")
        sys.exit(0)


if __name__ == '__main__':
    main()
