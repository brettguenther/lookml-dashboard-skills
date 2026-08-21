# LookML Dashboard Parameter Reference

This reference summarizes the key parameters used to build high-quality dashboards, as identified in the Looker demo environments.

## Dashboard-Level Parameters
| Parameter | Description | Recommended Usage |
| :--- | :--- | :--- |
| `layout: newspaper` | 24-column grid layout. | **Mandatory** for professional dashboards. |
| `preferred_viewer` | Viewer engine. | Use `dashboards-next` for the modern experience. |
| `style` | Dashboard styling theme. | Set to `modern` as default for all dashboards. |
| `crossfilter_enabled` | Enables click-to-filter. | Default is disabled. Only set to `true` when explicitly requested. |
| `auto_run` | Execution behavior. | Set to `false` if the dashboard has >15 heavy tiles. |
| `filters_bar_collapsed` | Initial filter state. | Set to `true` to focus on data first. |
| `filters_location_top` | Filter bar placement. | Set to `false` to move filters to the right sidebar. |
| `query_timezone` | Timezone for queries. | Always use `user_timezone`. |
| `tabs` | List of dashboard tabs. | Use to group elements by persona or topic. |

## Element-Level Parameters
| Parameter | Description | Best Practice |
| :--- | :--- | :--- |
| `type` | Visualization type. | Match type to the question (e.g., `looker_area` for trends). |
| `modern2026` | Modern 2026 visualization engine. | Set to `true` by default for all visualization types EXCEPT KPI (`single_value`) and maps. |
| `width` / `height` | Tile dimensions. | Use standard sizes (KPIs: 4x4, Trends: 12x8). |
| `row` / `col` | Tile position. | Maintain clear horizontal and vertical alignment. |
| `tab_name` | Tab assignment. | Must match a name defined in the top-level `tabs`. |
| `listen` | Filter mapping. | Ensure every tile "listens" to relevant dashboard filters. |
| `note` | Inline documentation. | Use `note_display: hover` for definitions. |
| `row_total` | Column-wise totals. | Use `right` to add a total column to grids. |
| `show_totals` | Display aggregate totals. | Essential for summary tables. |
| `reference_lines` | Static target lines. | Essential for providing context on trend charts. |
| `fill_fields` | Data gap filling. | Use for date dimensions to ensure trends have no breaks. |

## Filter Configuration (`ui_config`)
| Type | Display | Best Use Case |
| :--- | :--- | :--- |
| `button_group` | `inline` | Dimensions with 2-5 options (e.g., Gender). |
| `radio_buttons` | `popover` | Mutually exclusive options. |
| `dropdown_menu` | `popover` | Dimensions with many options (e.g., Brand). |
| `relative_timeframes` | `inline` | The primary date filter for the dashboard. |
| `advanced` | `popover` | For complex multi-select or string matching. |

## Visual Styling (`y_axes`)
- **Dual Axes**: Use two objects in the `y_axes` list with `orientation: left` and `orientation: right`.
- **Value Format**: Use `valueFormat: "$#,##0"` or similar for professional labels.
- **Log Scales**: Use `type: log` for metrics with extreme variance (e.g., population data).
