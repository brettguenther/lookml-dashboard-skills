# LookML Dashboard Element Vis Config: Single Value (`single_value`)

In Looker dashboards, **always default to `type: single_value`** for headline metrics, KPI cards, and summary numbers.

> [!IMPORTANT]
> - **Default Type**: `type: single_value` is the canonical visualization type for KPIs, scorecard metrics, and comparison cards.
> - **Single Record**: `type: looker_single_record` (or `single_record`) displays a key-value list of fields for a single database row, and must **only be used when explicitly requested by the user**.
> - **Engine Flag**: `single_value` and `single_record` do **NOT** use `modern2026: true`. Omit this flag on all single value elements.

---

## Options Reference Table (`type: single_value`)

| Option Key | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `show_single_value_title` | `boolean` (`true`/`false`) | `Show Title` | Toggle visibility of the card title label. Default is `true`. |
| `single_value_title` | `string` | `Title Override` | Custom text override for the element title. |
| `custom_color` | `string` (hex code) | `Value Color` | Hex color code for the primary metric value display (e.g. `"#1A73E8"`). |
| `value_format` | `string` | `Value Format` | Numeric display format pattern (e.g., `"$#,##0"`, `"$#,##0.00"`, `"0.0%"`). |
| `smart_single_value_size` | `boolean` (`true`/`false`) | `Auto Resize Value` | Dynamically scale font size to fit tile bounds. Recommended: `true`. |
| `show_comparison` | `boolean` (`true`/`false`) | `Show Comparison` | Display secondary comparison calculation beneath the primary metric. |
| `comparison_type` | `string` (`'change'`, `'progress_percentage'`) | `Comparison Type` | Comparison mode. `'change'` for Period-over-Period variance; `'progress_percentage'` for tracking against goals. |
| `comparison_label` | `string` | `Comparison Label` | Text label next to comparison value (e.g. `"vs Prior Month"`). |
| `comparison_reverse_colors` | `boolean` (`true`/`false`) | `Positive Values are Bad` | Invert green/red colors (set to `true` when decrease is good, like Wait Time or Unsubscribe Rate). |
| `show_comparison_label` | `boolean` (`true`/`false`) | `Show Comparison Label` | Toggle visibility of the comparison label text. |
| `comparison_row` | `number` | `Comparison Row` | Row index in query results used for comparison offset (default is `1` for the second row). |
| `comparison_series` | `string` | `Comparison Series` | Specific series identifier used for comparison offset. |
| `enable_conditional_formatting` | `boolean` (`true`/`false`) | `Enable Conditional Formatting` | Enable color rules based on metric thresholds. |
| `conditional_formatting_include_nulls_as_zero` | `boolean` (`true`/`false`) | `Include Null Values as Zero` | Treat null values as zero in conditional formatting checks. |
| `show_chart_component` | `boolean` (`true`/`false`) | `Show Chart Component` | Toggle display of an embedded mini sparkline beneath the KPI number. |
| `kpi_chart_type` | `string` | `Chart Type` | Mini sparkline visualization type (e.g. `line`, `area`). |
| `visible_x_axis` | `boolean` (`true`/`false`) | `Visible X Axis` | Toggle X-axis labels on embedded sparkline. |

---

## Production LookML Examples

### 1. Headline Revenue KPI with Period-over-Period Comparison
```yaml
- title: "Total Net Revenue"
  name: total_revenue_kpi
  model: thelook
  explore: order_items
  type: single_value
  fields: [order_items.total_sale_price, orders.created_month]
  filters:
    orders.created_date: "2 months ago for 2 months"
  sorts: [orders.created_month desc]
  limit: 2
  dynamic_fields:
    - table_calculation: pop_change
      label: "vs Prior Month"
      expression: "${order_items.total_sale_price} / offset(${order_items.total_sale_price}, 1) - 1"
      value_format_name: percent_1
  show_comparison: true
  comparison_type: change
  comparison_label: "vs Prior Month"
  comparison_reverse_colors: false
  custom_color: "#1A73E8"
  smart_single_value_size: true
  row: 0
  col: 0
  width: 6
  height: 4
```

### 2. Goal Tracking KPI (Progress Percentage)
```yaml
- title: "Quarterly Target Progress"
  name: quarterly_target_kpi
  model: thelook
  explore: order_items
  type: single_value
  fields: [order_items.total_sale_price]
  dynamic_fields:
    - table_calculation: target_progress
      label: "Goal Progress"
      expression: "${order_items.total_sale_price} / 1000000"
      value_format_name: percent_0
  show_comparison: true
  comparison_type: progress_percentage
  comparison_label: "of $1M Goal"
  custom_color: "#34A853"
  smart_single_value_size: true
  row: 0
  col: 6
  width: 6
  height: 4
```
