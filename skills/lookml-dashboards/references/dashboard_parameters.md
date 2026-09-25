# LookML Dashboard Parameter Reference

## This reference summarizes the key parameters used to build high-quality LookML dashboards.

## 1. Dashboard-Level Parameters

| Parameter             | Type      | Recommended Value | Description                                                                                          |
| :-------------------- | :-------- | :---------------- | :--------------------------------------------------------------------------------------------------- |
| `layout`              | `string`  | `newspaper`       | **Mandatory** for modern dashboards. Provides a 24-column grid for precise tile placement.           |
| `preferred_viewer`    | `string`  | `dashboards-next` | Uses the modern Looker rendering engine.                                                             |
| `style`               | `string`  | `modern`          | Applies modern UI layout styles.                                                                     |
| `crossfilter_enabled` | `boolean` | `false` (default) | Enables click-to-filter. Default to `false`; only set to `true` when explicitly requested.           |
| `auto_run`            | `boolean` | `true` or `false` | Set to `false` if the dashboard contains >15 heavy tiles to avoid overwhelming database connections. |
| `query_timezone`      | `string`  | `user_timezone`   | Queries execute in the viewing user's configured timezone.                                           |
| `tabs`                | `list`    | see below         | Groups elements into logical tabs. Each tab requires `name:` and `label:`.                           |

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
| **Histogram**          | `looker_histogram`       | Value frequency bins                       | ✅ **Required (`modern2026: true`)** |
| **Looker Grid**        | `looker_grid` / `table`  | Modern data table                          | ✅ **Required (`modern2026: true`)** |
| **Funnel**             | `looker_funnel`          | Multi-step dropoff conversion              | ✅ **Required (`modern2026: true`)** |
| **Timeline**           | `looker_timeline`        | Events & duration blocks                   | ✅ **Required (`modern2026: true`)** |
| **Word Cloud**         | `looker_wordcloud`       | Keyword density                            | ✅ **Required (`modern2026: true`)** |

---

## 4. Filter Configuration (`ui_config`)

| Type                  | Display   | Best Use Case                                                |
| :-------------------- | :-------- | :----------------------------------------------------------- |
| `dropdown_menu`       | `inline`  | Primary lookup dimension (5-50+ choices) on main filter bar. |
| `dropdown_menu`       | `popover` | Secondary segmentation filters to save screen space.         |
| `button_group`        | `inline`  | Short lists (2-4 items max, e.g. Tiers or Channels).         |
| `button_toggles`      | `inline`  | Binary choices (e.g. Yes/No, Active/Inactive).               |
| `relative_timeframes` | `inline`  | Standard primary date filter.                                |
| `advanced`            | `popover` | Complex string matches or numeric ranges.                    |

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
