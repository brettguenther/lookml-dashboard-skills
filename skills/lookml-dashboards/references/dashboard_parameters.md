# LookML Dashboard Parameter Reference

## This reference summarizes the key parameters used to build high-quality LookML dashboards.

## 1. Dashboard-Level Parameters

| Parameter                 | Type      | Recommended Value                   | Description                                                                                                                                                                   |
| :------------------------ | :-------- | :---------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `layout`                  | `string`  | `newspaper`                         | **Mandatory** for modern dashboards. Provides a 24-column grid (`default`) or 72-column grid (`granular`).                                                                    |
| `layout_granularity`      | `string`  | omit / `default` (`granular` opt-in)| Grid resolution: `'default'` (24 cols, 1x height) or `'granular'` (72 cols = `3x` width/col, `2x` height/row, min tile `6x4`). Keep coordinates consistent with chosen mode. |
| `preferred_viewer`        | `string`  | `dashboards-next` (or `dashboards`) | Uses the modern Looker rendering engine (`dashboards-next` or `dashboards`).                                                                                                  |
| `style`                   | `string`  | `modern`                            | Applies modern UI layout styles (`'modern'` or `'classic'`).                                                                                                                  |
| `tile_filter_information` | `string`  | `show_all` (when tile filters used) | Controls filter badge visibility on tiles: `'show_all'`, `'show_dashboard_only'` (default), or `'do_not_show'`. Set `'show_all'` when using `vis_filter: true`.               |
| `default_dashboard_agent` | `string`  | Model agent ID (optional)           | Binds a LookML conversational analytics agent (e.g., `agent_300`) to the dashboard; paired with optional `enabled_dashboard_agent: true`.                                    |
| `crossfilter_enabled`     | `boolean` | `false` (default)                   | Enables click-to-filter. Default to `false`; only set to `true` when explicitly requested.                                                                                    |
| `auto_run`                | `boolean` | `true` or `false`                   | Set to `false` if the dashboard contains >15 heavy tiles to avoid overwhelming database connections.                                                                          |
| `query_timezone`          | `string`  | `user_timezone`                     | Queries execute in the viewing user's configured timezone.                                                                                                                    |
| `tabs`                    | `list`    | see below                           | Groups elements into logical tabs. Each tab requires `name:` and `label:`.                                                                                                    |

---

## 2. Element-Level Parameters

| Parameter          | Type      | Best Practice                        | Description                                                                                                                                                                                        |
| :----------------- | :-------- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`             | `string`  | `snake_case` or text without periods | **Strict Rule**: Looker LookML compiler crashes if `name` contains a period (`.`). E.g., use `Revenue vs Cost`, never `Revenue vs. Cost`.                                                          |
| `type`             | `string`  | see table below                      | Visualization type. Default to `single_value` for KPIs, `looker_google_map` for maps.                                                                                                              |
| `modern2026`       | `boolean` | `true` (on supported types)          | **Critical Rendering Flag**: Must be set to `true` on all supporting visualization types (see allowlist below). Must be omitted on `single_value`, `looker_single_record`, and map visualizations. |
| `width` / `height` | `integer` | Grid units (24-col grid)             | Standard sizes: KPIs (4x4 or 6x4), Trends (12x8 to 24x8), Tables/Grids (24x10).                                                                                                                    |
| `row` / `col`      | `integer` | 24-column coordinates                | Maintain row alignment. If `tabs:` is used, reset `row: 0` at the start of each tab.                                                                                                               |
| `tab_name`         | `string`  | Matches `tabs[*].name`               | Assigns element to a specific tab. Required when `tabs:` is defined.                                                                                                                               |
| `listen`           | `map`     | `filter_name: field_name`            | Maps global dashboard filters to element query fields.                                                                                                                                             |
| `dynamic_fields`   | `list`    | Custom fields & calcs                | Defines table calculations, custom dimensions, and custom measures (see [Dynamic Fields Reference](dynamic_fields.md)).                                                                            |
| `note`             | `map`     | `note_display: hover`                | Inline metric definition documentation. Use `note_state: collapsed` and `note_display: hover`.                                                                                                     |
| `y_axes`           | `list`    | see below                            | Configures Y-axis scales. **Must** format nested `series` as a list of objects with `id` (`series: [{id: field}]`), never raw strings.                                                             |

---

## 3. Visualization Type & Engine Support Matrix

| Visualization Type     | LookML `type`            | Default Status                             | Supports `modern2026: true`?         |
| :--------------------- | :----------------------- | :----------------------------------------- | :----------------------------------- |
| **Single Value / KPI** | `single_value`           | **Default for all KPIs & summary numbers** | ❌ **Omit** (crashes or unsupported) |
| **Single Record**      | `looker_single_record`   | Only use if explicitly requested           | ❌ **Omit**                          |
| **Google Maps**        | `looker_google_map`      | **Default for all maps & geospatial data** | ❌ **Omit**                          |
| **Static Geo Regions** | `looker_geo_choropleth`  | Only use if explicitly requested           | ❌ **Omit**                          |
| **Static Geo Points**  | `looker_geo_coordinates` | Only use if explicitly requested           | ❌ **Omit**                          |
| **Column Chart**       | `looker_column`          | Standard category comparison               | ✅ **Required (`modern2026: true`)** |
| **Bar Chart**          | `looker_bar`             | Horizontal bars (long labels)              | ✅ **Required (`modern2026: true`)** |
| **Line Chart**         | `looker_line`            | Continuous time-series trends              | ✅ **Required (`modern2026: true`)** |
| **Area Chart**         | `looker_area`            | Cumulative/volume trends over time         | ✅ **Required (`modern2026: true`)** |
| **Scatterplot**        | `looker_scatter`         | Correlation / distribution                 | ✅ **Required (`modern2026: true`)** |
| **Waterfall**          | `looker_waterfall`       | Cumulative variance / walk                 | ✅ **Required (`modern2026: true`)** |
| **Boxplot**            | `looker_boxplot`         | Percentiles / distribution                 | ✅ **Required (`modern2026: true`)** |
| **Histogram**          | `looker_histogram`       | Value frequency / percent bins             | ✅ **Required (`modern2026: true`)** |
| **Bullet Chart**       | `looker_bullet`          | Actual vs target goal & qualitative bands  | ✅ **Required (`modern2026: true`)** |
| **Looker Grid**        | `looker_grid` / `table`  | Modern data table                          | ✅ **Required (`modern2026: true`)** |
| **Funnel**             | `looker_funnel`          | Multi-step dropoff conversion              | ✅ **Required (`modern2026: true`)** |
| **Timeline**           | `looker_timeline`        | Events & duration blocks                   | ✅ **Required (`modern2026: true`)** |
| **Word Cloud**         | `looker_wordcloud`       | Keyword density                            | ✅ **Required (`modern2026: true`)** |

---

## 4. Global & Tile-Scoped Filter Configuration (`ui_config` & `vis_filter`)

| Type                  | Display   | Scope                         | Best Use Case                                                |
| :-------------------- | :-------- | :---------------------------- | :----------------------------------------------------------- |
| `dropdown_menu`       | `inline`  | Dashboard bar                 | Primary lookup dimension (5-50+ choices) on main filter bar. |
| `dropdown_menu`       | `popover` | Dashboard bar or Tile filter  | Secondary segmentation filters or multi-option tile filters. |
| `button_group`        | `inline`  | Dashboard bar                 | Short lists (2-4 items max, e.g. Tiers or Regions).          |
| `button_group`        | `popover` | Tile filter (`vis_filter`)    | Compact interactive chip control rendered inside a tile.     |
| `tag_list`            | `popover` | Dashboard bar or Tile filter  | Multi-select tag token picker (`allow_multiple_values: true`).|
| `button_toggles`      | `inline`  | Dashboard bar                 | Binary choices (e.g. Yes/No, Active/Inactive).               |
| `relative_timeframes` | `inline`  | Dashboard bar                 | Standard primary date filter (`popover` if `vis_filter`).    |
| `advanced`            | `popover` | Dashboard bar or Tile filter  | Complex string matches or numeric ranges.                    |

### Tile-Scoped Filters (`vis_filter: true`) Compiler Rules (Looker 26.22+)

To attach a local filter bar directly inside a single visualization tile instead of the global dashboard header:

1. Declare the filter in top-level `filters:` with `vis_filter: true` (e.g., `name: "Traffic Source - User Behaviors by Traffic Source"`, `title: "Traffic Source"`).
2. Wire that filter name **only** inside the single target element's `listen:` map (`Traffic Source - User Behaviors by Traffic Source: users.traffic_source`).
3. Add `tile_filter_information: show_all` at the dashboard root so tile filter badges render clearly (for embedded dashboards, also ensure instance embed setting `embed_show_tile_filter_information: true`).
4. **Strict LookML Compiler Validation Rules (`HTDashboardValidator`)**:
   - **Single Element Only**: A `vis_filter: true` filter **cannot** be referenced in `listen:` by more than 1 element (compiler error).
   - **Queryable Tile Only**: Must bind to a query-based visualization or merge-query tile (never `type: text` or `button`).
   - **Never Required**: `required:` **must** be `false` (or omitted) — `required: true` throws a compiler error.
   - **No Filter Cascading**: `listens_to_filters:` **must** be empty (`[]`) or omitted — a `vis_filter` cannot listen to parent filters (compiler error).
   - **Popover Display Only**: `ui_config.display` **must** be `popover` (`display: inline` triggers a compiler warning).

```yaml
# Dashboard root
tile_filter_information: show_all

elements:
  - title: "User Behaviors by Traffic Source"
    name: "User Behaviors by Traffic Source"
    model: thelook
    explore: order_items
    type: looker_column
    modern2026: true
    fields: [users.traffic_source, order_items.average_sale_price, user_order_facts.average_lifetime_orders]
    listen:
      State: users.state
      Country: users.country
      Traffic Source - User Behaviors by Traffic Source: users.traffic_source
    row: 0
    col: 0
    width: 12
    height: 8

filters:
  - name: "Traffic Source - User Behaviors by Traffic Source"
    title: "Traffic Source"
    type: field_filter
    default_value: "Display,Email,Facebook,Organic,Search"
    allow_multiple_values: true
    required: false
    ui_config:
      type: button_group
      display: popover
    model: thelook
    explore: order_items
    listens_to_filters: []
    field: users.traffic_source
    vis_filter: true
```

---

## 5. Visual Styling (`y_axes`) Syntax Guardrail

When configuring `y_axes`, the nested `series` property **must** contain objects specifying `id`:

```yaml
# ✅ CORRECT: Object with id
y_axes:
  - label: "Total Revenue"
    orientation: left
    series:
      - id: order_items.total_sale_price
  - label: "Orders Count"
    orientation: right
    series:
      - id: orders.count

# ❌ WRONG: Passing raw strings throws JavaScript error "Cannot create property 'id' on string"
y_axes:
  - label: "Total Revenue"
    orientation: left
    series: [order_items.total_sale_price]
```
