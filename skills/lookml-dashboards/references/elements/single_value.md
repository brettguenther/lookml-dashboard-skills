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
| `custom_color` | `string` (hex code) | `Value Color` | (Optional) Hex color code for the primary metric value. Omit by default so tiles inherit uniform theme typography. |
| `value_format` | `string` | `Value Format` | Numeric display format pattern (e.g., `"$#,##0"`, `"$#,##0.00"`, `"0.0%"`). |
| `smart_single_value_size` | `boolean` (`true`/`false`) | `Auto Resize Value` | Dynamically scale font size to fit tile bounds. Recommended: `true`. |
| `primary_series` | `string` | `Primary Series` | (Optional) Field name or pivoted series ID (`"<pivotKey> - <fieldName>"`) for the headline KPI metric. Defaults to the leftmost measure in `fields:`. |
| `primary_row` | `string` (`'first'`, `'second'`, `'last'`, `'total'`) | `Primary Row` | Row in the query result (`KPI_ROW_SELECTION`) providing the headline KPI value. Defaults to `'first'`. |
| `show_comparison` | `boolean` (`true`/`false`) | `Show Comparison` | Display secondary comparison calculation beneath the primary metric. |
| `comparison_type` | `string` (`'value'`, `'change'`, `'change_percentage'`, `'progress'`, `'progress_percentage'`) | `Comparison Type` | Comparison mode: `'value'` (display as-is), `'change'` (absolute delta `primary - comparison`), `'change_percentage'` (`(primary - comparison) / \|comparison\|`), `'progress'` (progress bar + value), `'progress_percentage'` (progress bar + `%` of target). |
| `comparison_label` | `string` | `Comparison Label` | Text label next to comparison value (e.g. `"vs Prior Month (MTD)"`). |
| `comparison_reverse_colors` | `boolean` (`true`/`false`) | `Positive Values are Bad` | Invert green/red colors (set to `true` when decrease is good, like Wait Time or Unsubscribe Rate). |
| `show_comparison_label` | `boolean` (`true`/`false`) | `Show Comparison Label` | Toggle visibility of the comparison label text. |
| `comparison_row` | `string` (`'first'`, `'second'`, `'last'`, `'total'`) | `Comparison Row` | String enum (`KPI_ROW_SELECTION`) selecting which row provides the comparison baseline:<br>• **`'first'`**: Row 1 (`data[0]`). Use when comparing two **different** measures on Row 1 (`primary_series: measure_a`, `comparison_series: measure_b`), or when `primary_row: last` (ascending sort). Avoid setting both `primary_row: first` and `comparison_row: first` on the **same** series (compares a cell against itself = `0%`).<br>• **`'second'`**: Row 2 (`data[1]`). Standard for adjacent Period-over-Period when sorted descending (`Row 1` = current period, `Row 2` = prior period).<br>• **`'last'`**: Final row (`data[data.length - 1]`). Use when comparing `Row 1` against the oldest/baseline row in the window (e.g. `Row 13` for same-month YoY with `limit: 13`).<br>• **`'total'`**: Query Totals row (`totals_data`, requires `totals: true`). Use when comparing a row against the Grand Total (e.g. with `comparison_type: progress_percentage` for share of total). |
| `comparison_series` | `string` | `Comparison Series` | Field name (or pivoted series ID `"<pivotKey> - <fieldName>"`) of the measure or `dynamic_field` used for comparison (e.g. `'order_items.total_sale_price'`). Specify explicitly when `fields:` includes a leading timeframe dimension so Looker does not default comparison to the dimension column. |
| `enable_conditional_formatting` | `boolean` (`true`/`false`) | `Enable Conditional Formatting` | Enable color rules based on metric thresholds. |
| `conditional_formatting_include_nulls_as_zero` | `boolean` (`true`/`false`) | `Include Null Values as Zero` | Treat null values as zero in conditional formatting checks. |
| `show_chart_component` | `boolean` (`true`/`false`) | `Show Chart Component` | Toggle display of an embedded mini sparkline beneath the KPI number. |
| `kpi_chart_type` | `string` | `Chart Type` | Mini sparkline visualization type (e.g. `line`, `area`). |
| `visible_x_axis` | `boolean` (`true`/`false`) | `Visible X Axis` | Toggle X-axis labels on embedded sparkline. |

---

## Production LookML Examples

### 1. Headline Revenue KPI with Native Period-over-Period Comparison & Sparkline
No `offset()` table calculation is required for row-over-row comparison: sort the timeframe dimension descending (`Row 1` = current period, `Row 2` = prior period), set `comparison_series: <view.measure>`, `comparison_row: second`, and `comparison_type: change_percentage`. When Row 1 is an incomplete current month (Month-to-Date), filter by an `is_mtd: "Yes"` dimension (`EXTRACT(DAY FROM date) <= EXTRACT(DAY FROM CURRENT_DATE())`) so Row 2 and the sparkline compare equivalent elapsed days of each month:

```yaml
- title: "Total Net Revenue (MTD)"
  name: total_revenue_kpi
  model: thelook
  explore: order_items
  type: single_value
  fields: [orders.created_month, order_items.total_sale_price]
  filters:
    orders.created_date: "13 months"
    orders.is_mtd: "Yes"
  sorts: [orders.created_month desc]
  limit: 13
  show_comparison: true
  comparison_type: change_percentage
  comparison_series: order_items.total_sale_price
  comparison_row: second
  show_comparison_label: true
  comparison_label: "vs Prior Month (MTD)"
  comparison_reverse_colors: false
  show_chart_component: true
  kpi_chart_type: area
  visible_x_axis: false
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
  smart_single_value_size: true
  row: 0
  col: 6
  width: 6
  height: 4
```

---

## Custom LookML `html:` Sanitizer & Companion Measure Rules

When authoring custom LookML `html:` inside measures displayed in `type: single_value` tiles:
1. **CSS Flexbox Stripped by Sanitizer**: Looker's HTML sanitizer strips `display: flex`, `justify-content`, `align-items`, and `gap`.
2. **Line-Height & Letter-Spacing Inheritance**: `.single-value-value` inherits `line-height: ~48px` and negative `letter-spacing: -0.03em` while collapsing whitespace between inline tags. Always wrap custom multi-line HTML in `<div style="display: block; text-align: center; line-height: 1.3; letter-spacing: normal; padding: 2px 4px;">`, use `margin-top` for vertical spacing, and insert `&nbsp;&bull;&nbsp;` between inline spans.
3. **Companion Measure `_rendered_value` Formatting**: Referencing a secondary measure via `{{ other_measure._rendered_value }}` when `other_measure` is omitted from the tile's `fields:` list returns a raw unformatted float (`71.30075031...`). Pre-format companion stats in SQL (`FORMAT('$%.2f', ...)` or `FORMAT('%.1f%%', ...)`) inside a `hidden: yes` `type: string` helper measure and inject `{{ helper_measure._value }}`.
