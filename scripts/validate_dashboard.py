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
}


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

    for idx, elem in enumerate(elements):
        if not isinstance(elem, dict):
            continue
        ename = elem.get('name') or elem.get('title') or f"element_{idx}"
        etype = elem.get('type')

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
