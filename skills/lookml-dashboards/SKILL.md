---
name: "lookml-dashboards"
description: >-
  Designs, scaffolds, and optimizes LookML dashboards (.dashboard.lookml) on
  24-column or granular 72-column newspaper grids. Covers visual hierarchy,
  tabbed layouts, KPI scorecard cards, bullet charts (looker_bullet), histograms
  (looker_histogram), dynamic_fields (table calculations, custom dimensions, and
  custom measures), dual-axis mixed charts, looker_google_map parameters, global
  and tile-level filters (vis_filter: true, tile_filter_information), and rendering
  validation. Use when creating, editing, styling, refactoring, or auditing LookML
  dashboard YAML files. Don't use for LookML views/explores modeling (use lookml-view
  or lookml-explore) or React host application embedding code (use sso-embed).
---

# LookML Dashboard Best Practices

This skill distills the architectural requirements and visual standards for creating production-grade LookML dashboards. It is built to take advantage of all preview visualization and dashboard features available in Looker (`modern2026: true`, tile-scoped filters `vis_filter: true`, granular 72-column layout grids `layout_granularity: granular`, dashboard tile groups `type: group`, table hierarchy `row_groups` / `table_column_groups`, `looker_bullet`, and `looker_histogram`), with the expectation that these preview features are enabled in your Looker environment.

For element-specific options and technical details, see the reference guides:

- **Core References**: [Dashboard Parameter Reference](references/dashboard_parameters.md) | [Dynamic Fields (Custom Measures, Dimensions & Calcs)](references/dynamic_fields.md) | [Boilerplate Template](references/boilerplate_dashboard.md) | [Markdown & HTML Templates](references/markdown_html_templates.md)
- **Element Visualization Parameter References**:
  - [Single Value / KPI (`single_value`)](references/elements/single_value.md) *(Default for all KPI cards)*
  - [Bullet Chart (`looker_bullet`)](references/elements/bullet.md) *(Actual vs target goal & qualitative threshold bands)*
  - [Histogram (`looker_histogram`)](references/elements/histogram.md) *(Continuous frequency / percent bucket distributions)*
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

- **Dashboard-Level Parameters**: Always include `layout: newspaper`, `preferred_viewer: dashboards-next` (or `dashboards`), and `style: modern` as defaults. When tile-level filters (`vis_filter: true`) are present, set `tile_filter_information: show_all`. Optional `default_dashboard_agent: <agent_name>` binds a LookML-defined conversational analytics agent.
- **Identifier Naming Guardrail (Strict)**: Looker's LookML compiler strictly forbids periods (`.`) inside element `name:` and filter `name:` identifiers.
  - ✅ **Valid**: `name: revenue_vs_cost` or `name: "Traffic Source - User Behaviors"`
  - ❌ **Invalid**: `name: "Revenue vs. Cost"` (crashes LookML compiler)
- **Layout Method & Grid Granularity (`layout_granularity`)**:
  - **Default Grid (`layout: newspaper`)**: Uses a **24-column grid** (`rowHeight: 40`, min tile `width: 2`, `height: 1`). Use 24-column coordinates by default when authoring new dashboards.
  - **Granular Grid (`layout_granularity: granular`)**: High-resolution **72-column newspaper grid** (`3x` horizontal scale, `2x` vertical scale; min tile `width: 6`, `height: 4`). When editing or exporting a dashboard with `layout_granularity: granular`, row widths sum to `72` (e.g., `col: 0, width: 35` + `col: 35, width: 37`) and heights double (`height: 16` = `8` standard rows). Never mix 24-col and 72-col coordinates in the same dashboard.
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
- **Headline Styling**: Omit `custom_color` by default so KPI cards inherit the Looker theme's clean, uniform typography. Color is reserved for comparison deltas (`comparison_type: change` or `change_percentage`) or threshold-driven alerts (`enable_conditional_formatting: true`).
- **Single Record Constraint**: `type: looker_single_record` (or `single_record`) displays a single entity's raw field-value list and must **only be used when the user explicitly requests single record inspection**.
- **Engine Flag**: `type: single_value` and `type: looker_single_record` do **NOT** use `modern2026: true`. Omit this flag on all single value elements.
- **Comparison Types & Native Row-over-Row PoP**:
  - `comparison_type: change_percentage` or `change`: Best for Period-over-Period (MoM, YoY, WoW) analysis.
  - `comparison_type: progress_percentage` or `progress`: Best for tracking against linear goals.
  - **Native `comparison_row: second` (No Table Calc Needed)**: When a query returns `[timeframe_dim, measure]` sorted descending (`sorts: [orders.created_month desc]`, `limit: 2` or `limit: 13` with sparkline), Row 1 is the current period and Row 2 is the prior period. Configure `show_comparison: true`, `comparison_type: change_percentage`, `comparison_series: <view.measure>`, and `comparison_row: second` (string enum: `'first' | 'second' | 'last' | 'total'`). **Never set `comparison_row: first` when comparing the same measure sorted descending** (comparing Row 1 against Row 1 always renders `0%`).
  - **Apples-to-Apples MTD Filtering**: When Row 1 is an incomplete current month (Month-to-Date), filter the KPI tile by an `is_mtd: "Yes"` dimension (`EXTRACT(DAY FROM date) <= EXTRACT(DAY FROM CURRENT_DATE())`) so Row 2 (prior month) and any multi-month sparkline compare equivalent elapsed days of each month.
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
  - **Required on all supporting visualizations**: Cartesian charts (`looker_column`, `looker_bar`, `looker_line`, `looker_area`, `looker_scatter`, `looker_waterfall`, `looker_boxplot`, `looker_histogram`), bullet charts (`looker_bullet`), modern table (`looker_grid`, `table`), funnel (`looker_funnel`), timeline (`looker_timeline`), and word cloud (`looker_wordcloud`). Set `modern2026: true` at the element level.
  - **Must be omitted on**: KPI (`single_value`), single record (`looker_single_record`), and maps (`looker_google_map`, `looker_geo_choropleth`, `looker_geo_coordinates`).
  - **No Stale Cross-Type Properties**: Never carry over unrelated keys from another chart type (e.g., `bullet_*` keys on `looker_histogram`, or `show_value_labels` instead of `bullet_show_labels` on `looker_bullet`).
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

## 8. Global & Tile-Scoped Dashboard Filters

- **Global Filters**:
  - Prefer `type: field_filter` for automatic suggestion dropdowns.
  - `ui_config.display: inline`: Use for **primary, high-impact filters** that establish baseline context (date ranges, primary dimension lookup).
  - `ui_config.display: popover`: Use for **secondary filters** to maintain an uncluttered top bar.
  - Control types: `dropdown_menu` (long lists), `tag_list` (multi-select tags), `button_group` (2-5 items), `button_toggles` (binary Yes/No), `relative_timeframes` (primary dates), `advanced` (complex conditions).
- **Filters on Tiles (`vis_filter: true` — Looker 26.22+)**:
  - Render an interactive filter chip bar directly inside an individual visualization tile instead of filtering the entire dashboard:
    1. Define the filter in top-level `filters:` with `vis_filter: true` (conventionally naming `name: "<Filter Title> - <Element Title>"` and short `title: "<Filter Title>"`, with no periods).
    2. Bind it inside **only** that single target element's `listen:` map (`<filter_name>: <view.field>`).
    3. Set `tile_filter_information: show_all` at the dashboard root (`'show_all'`, `'show_dashboard_only'`, or `'do_not_show'`; embedded dashboards also require instance setting `embed_show_tile_filter_information: true`).
  - **Strict Compiler Rules (`HTDashboardValidator`)**:
    - A `vis_filter: true` filter **must only be listened to by 1 query-based visualization element** (sharing across 2+ tiles is a LookML compiler error).
    - **Must set `required: false`** (`required: true` is a compiler error).
    - **Cannot cascade** (`listens_to_filters: []` or omit — listening to parent filters is a compiler error).
    - **Must use `ui_config.display: popover`** (`display: inline` triggers a compiler warning).

---

## 9. Advanced Markdown (Header & Branding Tiles)

Use `type: text` tiles for branding, subtitles, and section headers. See [Markdown & HTML Templates](references/markdown_html_templates.md) for copy-paste templates.

---

## 10. Dashboard Tile Groups (`type: group` & `group:`)

Dashboard Tile Groups group multiple elements (e.g. scorecard KPIs, dual charts, or related tables) into a unified visual container box with an optional header banner and subtitle.

### Compiler & Layout Invariants

1. **Relative Internal Coordinates**: Child elements that belong to a group (`group: <group_container_name>`) specify coordinates (`row`, `col`) **relative to the inside of the group container** (starting at `0, 0`).
2. **Container Height Bounds**: The parent group container's `height` must be large enough to enclose all child elements (`container_height >= header_height + max_child_bottom`).
3. **Tab Scoping**: A child element and its parent `type: group` container **must reside on the same tab** (`tab_name`).
4. **No Nested Groups**: A child element cannot itself be a `type: group` container.
5. **No Periods in Names**: The group `name` cannot contain periods (`.`).

```yaml
elements:
  - name: kpi_summary_group
    type: group
    title: "Executive KPIs (Tile Group Container)"
    subtitle_text: "Topline business performance indicators"
    title_hidden: false
    row: 0
    col: 0
    width: 24
    height: 6

  - name: revenue_kpi
    group: kpi_summary_group            # Links to parent group container name
    type: single_value
    model: thelook
    explore: order_items
    fields: [order_items.total_sale_price]
    row: 0                              # Relative row inside container
    col: 0                              # Relative col inside container
    width: 8
    height: 4
```

---

## 11. Table Hierarchy Grouping & Collapsible Columns

Modern `looker_grid` / `table` visualizations (`modern2026: true`) support multi-level collapsible row trees, per-hierarchy tier styling, and multi-column grouping banners:

### Key Rules & Invariants

1. **Row Hierarchy (`row_groups`)**:
   - `row_grouping_fields: [dim_parent, dim_child]`: Ordered list of dimension field names collapsed into the tree hierarchy auto-column.
   - `default_display_level`: Must be one of `'collapsed'`, `'top_expanded'`, or `'all_expanded'`.
   - `show_grouped_columns: false`: Merges dimensions into the auto-column tree and hides redundant separate columns.
   - **Mutual Exclusivity**: `row_groups.enabled: true` is **disabled if pagination is active (`table_enable_pagination: true`) or sparklines are active (`table_sparklines.enabled: true`)**.
   - **Subtotal Rollup Semantics**: When `configurable_subtotals: true`, AG Grid calculates client-side subtotals **only for `sum` and `count` measures**. Averages and complex measures render blank to prevent mathematically invalid rollups.
   - **Per-Tier Styling**: Applying `series_text_format.<dimension_name>` to any grouped dimension in `row_grouping_fields` styles **that exact hierarchy depth tier** in the tree auto-column.
2. **Column Groups (`table_column_groups`)**:
   - Creates multi-tier parent header banners across multiple child columns.
   - **Mutual Exclusivity**: Column groups are **disabled when query `pivots` are present or `transpose: true`**.

```yaml
vis_config:
  type: looker_grid
  modern2026: true
  header_font_size: 12                  # Must be integer pixels, NOT string
  rows_font_size: 12                    # Must be integer pixels, NOT string
  row_groups:
    enabled: true
    row_grouping_fields:
      - products.department             # Level 0 (outer tree node)
      - products.category               # Level 1 (nested child node)
    default_display_level: all_expanded # 'collapsed' | 'top_expanded' | 'all_expanded'
    group_column_header: "Merchandising Hierarchy"
    show_group_counts: true             # Shows '(N)' child row counts
    configurable_subtotals: true        # Client-side rollup on sum/count measures
    show_grouped_columns: false
  table_column_groups:
    enabled: true
    defaultDisplayState: expanded
    namespaceCsvHeaders: true
    groups:
      - id: fulfillment_volume
        title: "Fulfillment & Volume"
        columns: [order_items.status, order_items.count]
        defaultDisplayState: expanded
        collapsedVisibleColumns: [order_items.count]
        headerBackgroundColor: "#1a73e8"
        headerTextColor: "#ffffff"
  series_text_format:
    products.department:                # Styles Level 0 nodes
      bold: true
      fg_color: "#174ea6"
      bg_color: "#e8f0fe"
    products.category:                  # Styles Level 1 nodes
      bold: true
      fg_color: "#0d652d"
      bg_color: "#e6f4ea"
```

---

## 12. Performance and Interactivity

- **Cross-Filtering (`crossfilter_enabled`)**: Cross-filtering is **disabled by default** (`crossfilter_enabled: false`). Only set `crossfilter_enabled: true` when explicitly requested **AND** 100% of query tiles on the dashboard reference the **exact same `(model, explore)` pair**. Enabling `crossfilter_enabled: true` on a multi-explore dashboard triggers Looker's `"Unable to cross-filter. Tiles from multiple explores have been added to this dashboard."` warning banner.
- **Tile Notes**: Provide metric definitions using `note_state: collapsed` and `note_display: hover`.
- **Auto Run**: Set `auto_run: false` for dashboards with >15 heavy analytical tiles.
- **Query Timezone**: Always use `query_timezone: user_timezone`.

---

## 13. Dashboard Quality Checklist

- [ ] Uses `newspaper` layout (24-col default or consistent 72-col `layout_granularity: granular`) with `style: modern` and `preferred_viewer: dashboards-next`.
- [ ] No periods (`.`) in any element `name` or filter `name` identifiers.
- [ ] Every KPI card defaults to `type: single_value` (only use `single_record` if explicitly requested).
- [ ] Maps default to `type: looker_google_map` (`looker_geo_*` used only if explicitly requested).
- [ ] `modern2026: true` is set on all supporting visualizations (cartesian, histogram, bullet, grid/table, funnel, timeline, wordcloud).
- [ ] `modern2026` is omitted on `single_value`, `looker_single_record`, `type: group`, and map visualizations.
- [ ] Any `type: group` element defines container `width` and `height`, and all child elements specify `group: <group_name>` using relative `row` and `col` coordinates (starting at `0, 0` inside the container).
- [ ] Any table with `row_groups.enabled: true` specifies `row_grouping_fields: [...]`, uses `'collapsed' | 'top_expanded' | 'all_expanded'` for `default_display_level`, sets integer pixel font sizes (`header_font_size: 12`, `rows_font_size: 12`), and omits pagination and sparklines.
- [ ] Any table with `table_column_groups.enabled: true` omits query `pivots` and `transpose: true`.
- [ ] Any tile-scoped filter (`vis_filter: true`) uses `ui_config.display: popover`, `required: false`, `listens_to_filters: []`, binds to exactly 1 visualization element in `listen:`, and pairs with `tile_filter_information: show_all`.
- [ ] If `tabs:` is defined, every element specifies `tab_name`, and each tab starts at `row: 0`.
- [ ] All `y_axes` entries format `series` as a list of objects (`- id: field_name`), never raw strings.
- [ ] Every Period-over-Period KPI has descending sort on the date dimension (`limit: 2`).
- [ ] Elements joining nullable dimensions have explicit `-NULL` filters to prevent unmapped groupings.
