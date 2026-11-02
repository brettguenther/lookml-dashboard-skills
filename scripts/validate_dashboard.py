#!/usr/bin/env python3
"""LookML Dashboard Validator

Validates LookML dashboard files (*.dashboard.lookml) against fatal rendering
and compiler constraints.

Omit stylistic constraints — only checks conditions expected to break rendering.
"""

import sys
import os
import argparse
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


def validate_dashboard_dict(dash, filepath):
    errors = []
    dash_name = dash.get('dashboard') or dash.get('title') or 'unnamed_dashboard'
    
    # 1. Check declared tabs
    declared_tabs = set()
    if 'tabs' in dash and isinstance(dash['tabs'], list):
        for tab in dash['tabs']:
            if isinstance(tab, dict) and 'name' in tab:
                declared_tabs.add(tab['name'])

    # 2. Check filters for fatal period (.) in name
    if 'filters' in dash and isinstance(dash['filters'], list):
        for f in dash['filters']:
            if isinstance(f, dict):
                fname = f.get('name', '')
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

        # Check single_value comparison_row validity
        if etype == 'single_value' and elem.get('show_comparison'):
            comp_row = elem.get('comparison_row')
            if comp_row is not None:
                if not isinstance(comp_row, str) or comp_row not in VALID_COMPARISON_ROWS:
                    errors.append(
                        f"[{dash_name} -> {ename}] Invalid 'comparison_row: {comp_row}'. "
                        f"Must be one of {sorted(VALID_COMPARISON_ROWS)} (use 'second' for Row 1 vs Row 2 PoP)."
                    )
                elif comp_row == 'first' and not elem.get('dynamic_fields'):
                    sorts = elem.get('sorts') or []
                    if any('desc' in str(s).lower() for s in sorts):
                        errors.append(
                            f"[{dash_name} -> {ename}] 'comparison_row: first' with descending sort and no dynamic_fields "
                            "compares Row 1 against Row 1 (0% change). Set 'comparison_row: second' for Row 1 vs Row 2 PoP."
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
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
    except Exception as e:
        return [f"YAML parse error in {filepath}: {e}"]

    if not content:
        return [f"File {filepath} is empty."]

    dashboards = content if isinstance(content, list) else [content]
    all_errors = []
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
