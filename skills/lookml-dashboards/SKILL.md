---
name: "lookml-dashboards"
description: >-
  Designs, scaffolds, and optimizes LookML dashboards (.dashboard.lookml) on a
  24-column newspaper grid. Covers visual hierarchy, tabbed layouts, KPI scorecard
  cards, dynamic_fields (table calculations, custom dimensions, and custom measures),
  dual-axis mixed charts, looker_google_map parameters, ui_config filter bars,
  and rendering validation. Use when creating, editing, styling, refactoring, or
  auditing LookML dashboard YAML files. Don't use for LookML views/explores modeling
  (use lookml-view or lookml-explore) or React host application embedding code
  (use sso-embed).
---

# LookML Dashboard Best Practices

This skill distills the architectural requirements and visual standards for creating production-grade LookML dashboards.

For element-specific options and technical details, see the reference guides:

- **Core References**: [Dashboard Parameter Reference](references/dashboard_parameters.md) | [Dynamic Fields (Custom Measures, Dimensions & Calcs)](references/dynamic_fields.md) | [Boilerplate Template](references/boilerplate_dashboard.md) | [Markdown & HTML Templates](references/markdown_html_templates.md)
- **Element Visualization Parameter References**:
  - [Single Value / KPI (`single_value`)](references/elements/single_value.md) *(Default for all KPI cards)*
  - [Google Maps (`looker_google_map`)](references/elements/map.md) *(Default for all maps)*
  - [Cartesian (Line, Bar, Column, Area, Scatter, Waterfall, Boxplot)](references/elements/cartesian.md)
  - [Table & Grid (`looker_grid`)](references/elements/table.md)
  - [Conditional Formatting Syntax](references/elements/conditional_formatting.md)
  - [Funnel & Stepped Funnel](references/elements/funnel.md)
  - [Timeline](references/elements/timeline.md)
  - [Word Cloud](references/elements/wordcloud.md)
  - [Single Record (`looker_single_record`)](references/elements/single_record.md) *(Only when explicitly requested)*

> [!IMPORTANT]
> **Agent Execution Directive**: When building or modifying a specific dashboard element's YAML configuration (such as chart axes, series types, map styles, table formatting, or KPI comparisons), you **MUST** view the corresponding reference file under `references/elements/<vis_type>.md` (relative to this `SKILL.md`) to look up exact allowed property names, data types, and YAML nesting rules.

---

## 1. Dashboard Layout and Structure

- **Dashboard-Level Parameters**: Always include `layout: newspaper`, `preferred_viewer: dashboards-next`, and `style: modern` as defaults.
- **Identifier Naming Guardrail (Strict)**: Looker's LookML compiler strictly forbids periods (`.`) inside element `name:` and filter `name:` identifiers.
  - ✅ **Valid**: `name: revenue_vs_cost` or `name: "Revenue vs Cost"`
  - ❌ **Invalid**: `name: "Revenue vs. Cost"` (crashes LookML compiler)
- **Layout Method**: Standardize on `layout: newspaper`. It provides a 24-column grid for flexible element positioning.
- **Sectioning**: Use `type: text` elements as section headers to create a visual narrative (`width: 24`, `height: 3`).
- **Visual Hierarchy**: Place high-level KPIs across the top row, followed by trend visualizations, and detailed breakdowns/tables at the bottom.
- **Element Sizing & Row Height Alignment**:
  - **Uniform Row Heights**: Tiles placed on the same row (`row: N`) MUST share the exact same `height` (e.g. four KPI cards with `width: 6, height: 4` spanning the full 24 columns). NEVER mix short KPI cards (height 3-4) and tall bar/line charts (height 7-8) side-by-side in the same row.
  - **KPIs**: Typically `width: 4` to `8` and `height: 4` arranged uniformly across row 0 or directly beneath the header.
  - **Trends (Area/Line)**: Typically `width: 12` to `24` and `height: 6` to `8` in dedicated rows.
  - **X-Axis Label Density**: For dense time-series or categorical bars with long labels, configure `x_axis_label_rotation: -45` to prevent text truncation and overlapping labels.
  - **High-Contrast Categorical Color Palettes**: When plotting categorical series (e.g., browsers, devices, marketing channels), avoid muted or adjacent shades; use high-contrast modern palettes (`["#4285F4", "#34A853", "#FBBC05", "#EA4335", "#12B5CB", "#7B1FA2"]`) so series remain immediately distinguishable.

---

## 2. Tabs Implementation

Tabs organize complex dashboards into logical sections (e.g., "Executive Summary", "Operational Details").

- **Dashboard Level**:
  ```yaml
  tabs:
    - name: executive_summary
      label: "Executive Summary"
    - name: operational_details
      label: "Operational Details"
  ```
- **Element Level**: Assign elements to tabs using the `tab_name` parameter.
- **Tab Coordinate Isolation**: Each tab maintains its own independent vertical layout grid. **Always reset `row: 0` for the top elements of each respective tab**.

---

## 3. KPI Cards & Single Value Defaults

- **Default Visualization Type**: **Always default to `type: single_value`** for KPI scorecard tiles, headline metrics, and summary numbers.
- **Single Record Constraint**: `type: looker_single_record` (or `single_record`) displays a single entity's raw field-value list and must **only be used when the user explicitly requests single record inspection**.
- **Engine Flag**: `type: single_value` and `type: looker_single_record` do **NOT** use `modern2026: true`. Omit this flag on all single value elements.
- **Comparison Types**:
  - `comparison_type: change`: Best for Period-over-Period (YoY, WoW) analysis.
  - `comparison_type: progress_percentage`: Best for tracking against linear goals.
- **PoP Sorting Prerequisite**: When calculating Period-over-Period change via `offset(${measure}, 1)`, **always sort the date dimension in descending order** (`sorts: [orders.created_month desc]`) with `limit: 2` so `offset(..., 1)` references the earlier period.
- **Reverse Colors**: Set `comparison_reverse_colors: true` for metrics where a decrease is positive (e.g., Wait Time, Bounce Rate).

---

## 4. Advanced Analytics & Dynamic Fields

Looker dashboards support three distinct categories of `dynamic_fields`:

### A. Custom Dimensions (`category: dimension`)
Evaluated in SQL on each row before aggregation, enabling ad-hoc bucketing, string concatenation, or math:
```yaml
dynamic_fields:
  - dimension: user_full_name
    label: "Customer Full Name"
    expression: 'concat(${users.first_name}, " ", ${users.last_name})'
    category: dimension
    _kind_hint: dimension
    _type_hint: string
```

### B. Custom Measures & Filtered Measures (`category: measure`)
Evaluated in SQL as aggregate functions with optional filter expressions:
```yaml
dynamic_fields:
  - measure: cancelled_orders_count
    label: "Cancelled Orders"
    based_on: orders.id
    type: count_distinct
    filter_expression: '${orders.status} = "cancelled"'
    category: measure
    _kind_hint: measure
    _type_hint: number
```

### C. Table Calculations (`table_calculation:`)
Evaluated in the browser over the returned result set for post-query analysis:
- **Period-over-Period (PoP)**: `expression: "${revenue} / offset(${revenue}, 1) - 1"`
- **Cumulative Trends**: `expression: "running_total(${revenue})"`
- **Share of Total**: `expression: "${count} / sum(${count})"`
- **Partial Period Suppression**: `expression: "if(${created_date} <= now(), ${count}, null)"`

See [Dynamic Fields Reference](references/dynamic_fields.md) for full syntax and recipes.

---

## 5. Mixed Series and Dual Axes

Correlate different metric types (e.g., Sessions and Conversion Rate) in one tile.

- **Series Types**: Override specific series using `series_types`.
  ```yaml
  series_types:
    sessions.overall_conversion: line
    events.sessions_count: column
  ```
- **Dual Axes**: Configure `y_axes` with left and right orientations to handle different scales.
  > [!IMPORTANT]
  > When configuring `y_axes`, the nested `series` parameter **must** contain a list of objects specifying `id` (and optionally `name`), rather than a list of simple strings. Passing plain strings causes a fatal JavaScript error: `"Cannot create property 'id' on string '...'"`:
  ```yaml
  y_axes:
    - label: "Left Axis"
      orientation: left
      series:
        - id: events.sessions_count
          name: "Sessions Count"
    - label: "Right Axis"
      orientation: right
      series:
        - id: sessions.overall_conversion
          name: "Conversion Rate"
  ```
- **Data Totals**: For `looker_grid` and `looker_column`, enable `show_totals: true` where appropriate.

---

## 6. Styling and Modern Engine Rules (`modern2026: true`)

- **Modern 2026 Engine (`modern2026: true`)**:
  - **Required on all supporting visualizations**: Cartesian charts (`looker_column`, `looker_bar`, `looker_line`, `looker_area`, `looker_scatter`, `looker_waterfall`, `looker_boxplot`, `looker_histogram`), modern table (`looker_grid`, `table`), funnel (`looker_funnel`), timeline (`looker_timeline`), and word cloud (`looker_wordcloud`). Set `modern2026: true` at the element level.
  - **Must be omitted on**: KPI (`single_value`), single record (`looker_single_record`), and maps (`looker_google_map`, `looker_geo_choropleth`, `looker_geo_coordinates`).
- **Monotone Interpolation**: For line/area charts, use `interpolation: monotone` for a modern, smooth visual curve.
- **Consistent Coloring**: Define `series_colors` for categorical dimensions so brand/entity colors remain consistent across all tiles.
- **Advanced Grid Styling**:
  - **Cell Visualizations**: Use `series_cell_visualizations` to embed bar charts in table cells for metrics.
  - **Size to Fit**: Use `size_to_fit: true` so table columns dynamically fill the container width.

---

## 7. Geospatial Visualizations (Google Maps Default)

- **Default Map Engine**: **Always use `type: looker_google_map`** as the default for all geographic and location data.
- **Static Maps Limitation**: `looker_geo_choropleth` (static TopoJSON regions) and `looker_geo_coordinates` (static point charts) render static assets and should **only be used if explicitly requested**.
- **Engine Flag**: Maps do **not** take `modern2026: true`.
- **Core Google Map Parameters**:
  - `map_tile_provider`: Style theme (`'light'`, `'light_no_labels'`, `'dark'`, `'dark_no_labels'`, `'satellite'`, `'satellite_streets'`, `'streets'`, `'traffic_day'`, `'traffic_night'`). Default is `'light'`.
  - `map_position`: Set to `'fit_data'` to auto-center on query results, or `'custom'` with `map_latitude`, `map_longitude`, and `map_zoom` (0-22).
  - `map_marker_type`: `'circle'`, `'icon'`, `'circle_and_icon'`, `'none'`.
  - `map_marker_radius_mode`: `'proportional_value'`, `'equal_to_value'`, `'fixed'`. Set `map_marker_radius_min: 3` and `map_marker_radius_max: 18` for clean proportion scaling.
  - `map_value_colors`: Gradient color array for value-based shading.
  - `map_traffic_layer`, `map_transit_layer`, `map_bicycling_layer`: Real-time Google Maps overlays.
  - `draw_map_labels_above_data: true`: Renders street/city labels on top of data layers on `'light'`, `'dark'`, and `'satellite_streets'`.

See [Google Maps Parameter Reference](references/elements/map.md) for complete options and recipes.

---

## 8. Dashboard Filters

- **Filter Type**: Prefer `type: field_filter` for automatic suggestion dropdowns.
- **UI Configuration (`ui_config`)**:
  - `display: inline`: Use for **primary, high-impact filters** that establish baseline context (date ranges, primary dimension lookup).
  - `display: popover`: Use for **secondary filters** to maintain an uncluttered top bar.
  - Control types: `dropdown_menu` (long lists), `button_group` (2-4 items), `button_toggles` (binary Yes/No), `relative_timeframes` (primary dates), `advanced` (complex conditions).

---

## 9. Advanced Markdown (Header & Branding Tiles)

Use `type: text` tiles for branding, subtitles, and section headers. See [Markdown & HTML Templates](references/markdown_html_templates.md) for copy-paste templates.

---

## 10. Performance and Interactivity

- **Cross-Filtering**: Cross-filtering is **disabled by default**. Only set `crossfilter_enabled: true` when explicitly requested.
- **Tile Notes**: Provide metric definitions using `note_state: collapsed` and `note_display: hover`.
- **Auto Run**: Set `auto_run: false` for dashboards with >15 heavy analytical tiles.
- **Query Timezone**: Always use `query_timezone: user_timezone`.

---

## 11. Dashboard Quality Checklist

- [ ] Uses `newspaper` layout on a 24-column grid with `style: modern` and `preferred_viewer: dashboards-next`.
- [ ] No periods (`.`) in any element `name` or filter `name` identifiers.
- [ ] Every KPI card defaults to `type: single_value` (only use `single_record` if explicitly requested).
- [ ] Maps default to `type: looker_google_map` (`looker_geo_*` used only if explicitly requested).
- [ ] `modern2026: true` is set on all supporting visualizations (cartesian, grid/table, funnel, timeline, wordcloud).
- [ ] `modern2026` is omitted on `single_value`, `looker_single_record`, and map visualizations.
- [ ] If `tabs:` is defined, every element specifies `tab_name`, and each tab starts at `row: 0`.
- [ ] All `y_axes` entries format `series` as a list of objects (`- id: field_name`), never raw strings.
- [ ] Every Period-over-Period KPI has descending sort on the date dimension (`limit: 2`).
- [ ] Elements joining nullable dimensions have explicit `-NULL` filters to prevent unmapped groupings.
