# LookML Dashboard Element Vis Config: Histogram (`looker_histogram`)

Histogram visualizations (`type: looker_histogram`) group continuous numeric observations into automatic or custom-sized interval buckets to display frequency counts or percentage distributions.

> [!IMPORTANT]
> - **Modern Engine Required**: Always include `modern2026: true` on `looker_histogram` elements.
> - **Query & Binning Validation (`validateHistogram`)**:
>   - **Numeric Data Requirement**: Query results **must** include at least one numeric field (`measure` or numeric `dimension`) containing valid numeric values (`binning_field` explicitly selects which field to bin).
>   - **Row Limit for Distribution Fidelity**: Histograms bin returned rows client-side (`HistogramMapper`). Set `limit: 5000` when binning entity-level observations (e.g., `[order_items.order_count, order_facts.order_amount]`) so the distribution is not truncated at 500 rows.
>   - **Pivoted Histograms**: Optional `1` pivot dimension is supported for stacked/percent distributions, **provided at least 1 measure is present** (`"Pivoted histogram visualizations require at least one measure."`).
>   - **Bin Bounds Rules**: If specified, `binsNumber` **must** be an integer `>= 1`, and `binWidth` **must** be strictly `> 0`.
> - **Clean LookML Hygiene**: Set `column_spacing_ratio: 0` and `column_group_spacing_ratio: 0` for contiguous histogram bars, and omit unrelated `bullet_*`, `point_style`, or `interpolation` keys.

---

## Options Reference Table (`type: looker_histogram`)

### Binning, Display Mode & Plot Options

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `modern2026` | `boolean` (`true`) | `Modern 2026 Engine` | Enable Modern 2026 styling engine. **Recommended: `true`**. |
| `binning_field` | `string` | `Field to Bin` | Fully qualified field name (`view.field_name`) whose numeric values are bucketed along the X-axis (defaults to first numeric measure/dimension). |
| `binsNumber` | `number` (integer `>= 1`) | `Number of Bins` | Explicit number of histogram buckets. Must be a whole number `> 0` (omit for automatic pretty binning). |
| `binWidth` | `number` (`> 0`) | `Bin Width` | Explicit numeric width of each interval bucket. Must be `> 0` (omit for automatic bin sizing). |
| `bin_range_format` | `string` (`'bracket'`, `'to'`, `'relational'`, `'range'`) | `Bin Range Style` | Interval formatting style used in tooltips and interval X-axis labels: `'bracket'` (`"[x, y)"`, default), `'to'` (`"x to y"`), `'relational'` (`">=x and <y"`), or `'range'` (`"x - y"`). |
| `x_axis_bin_label_format` | `string` (`'interval'`, `'single'`) | `Bin Label Format` | Format X-axis bucket labels as full intervals inheriting `bin_range_format` (`'interval'`, default) or single boundary values (`'single'`). |
| `y_axis_mode` | `string` (`'count'`, `'percent'`) | `Display Mode` | Plot raw bucket frequencies (`'count'`, default) or share of total observations (`'percent'`). |
| `column_spacing_ratio` | `number` (`0` to `1`) | `Inner Spacing` | Inner column spacing ratio. Default is `0` (contiguous histogram bars). |
| `column_group_spacing_ratio` | `number` (`0` to `1`, step `0.1`) | `Spacing` | Gap ratio between adjacent histogram bin bars. Default is `0` (`0` for classic zero-gap histogram). |
| `stacking` | `string` (`'normal'`, `'percent'`) | `Stacking` | Stacking mode when a `pivots:` dimension is present (`'normal'` stacked or `'percent'` 100% stacked; default `'normal'`). |
| `show_value_labels` | `boolean` (`true`/`false`) | `Show Value Labels` | Render frequency/percent values directly above histogram bars. Default is `false`. |
| `reference_lines` | `array` of `object` | `Reference Lines` | Statistical or static reference lines/bands (`mean`, `median`, `deviation`, or fixed value). |
| `limit_displayed_rows` | `boolean` (`true`/`false`) | `Limit Displayed Rows` | Restrict displayed rows before binning (`false` by default). |
| `limit_displayed_rows_values` | `object` | `Limit Displayed Rows Values` | `{ show_hide: 'hide'|'show', first_last: 'first'|'last', num_rows: '10' }`. |

### Axes, Labels & Styling Options

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `min` / `max` | `number` | `Min Bound / Max Bound` | Explicit lower and upper numeric bounds on the binned X-axis domain. |
| `show_x_axis_label` | `boolean` (`true`/`false`) | `Show X Axis Title` | Toggle X-axis title visibility. Default is `true`. |
| `x_axis_label` | `string` | `X Axis Custom Title` | Custom title text for the binned X-axis (defaults to binned field label). |
| `show_x_axis_ticks` | `boolean` (`true`/`false`) | `Axis Value Labels` | Show bin interval labels on the X-axis. Default is `true`. |
| `x_axis_value_format` | `string` | `Value Format` | Number format pattern applied to X-axis bin boundaries (e.g., `"$#,##0"`). |
| `x_axis_label_rotation` | `number` (`-360` to `360`) | `Label Rotation` | Rotate X-axis interval labels in degrees (e.g., `-45` when `bin_range_format: to` produces wide labels). |
| `x_axis_gridlines` | `boolean` (`true`/`false`) | `X Axis Gridlines` | Toggle vertical X-axis gridlines. Default is `false`. |
| `x_axis_reversed` | `boolean` (`true`/`false`) | `Reverse Axis` | Reverse X-axis direction. Default is `false`. |
| `x_axis_zoom` | `boolean` (`true`/`false`) | `X Axis Zoom` | Allow interactive drag-to-zoom along X-axis. Default is `true`. |
| `show_y_axis_labels` | `boolean` (`true`/`false`) | `Show Y Axis Title` | Toggle Y-axis title visibility. Default is `true`. |
| `y_axis_labels` | `array` of `string` | `Y Axis Custom Title` | Custom Y-axis title array (e.g., `["Percent of Orders"]`). |
| `show_y_axis_ticks` | `boolean` (`true`/`false`) | `Axis Value Labels` | Toggle Y-axis tick values. Default is `true`. |
| `y_axis_scale_mode` | `string` (`'linear'`, `'log'`) | `Scale Type` | Linear (`'linear'`, default) or logarithmic (`'log'`) Y-axis scale. |
| `y_axis_tick_density` | `string` (`'default'`, `'custom'`) | `Tick Density` | Y-axis tick spacing mode (`'default'` or `'custom'`). |
| `y_axis_tick_density_custom` | `number` (`2` to `25`) | `Custom Tick Density` | Tick count slider when `y_axis_tick_density: custom`. Default is `5`. |
| `y_axis_gridlines` | `boolean` (`true`/`false`) | `Y Axis Gridlines` | Toggle horizontal Y-axis gridlines. Default is `true`. |
| `y_axis_reversed` | `boolean` (`true`/`false`) | `Reverse Axis` | Reverse Y-axis direction. Default is `false`. |
| `y_axis_zoom` | `boolean` (`true`/`false`) | `Y Axis Zoom` | Allow interactive vertical zoom. Default is `true`. |
| `color_application` | `object` | `Color Configuration` | Discrete color palette (`collection_id`, `palette_id`, `options`). |
| `hide_legend` | `boolean` (`true`/`false`) | `Hide Legend` | Hide series legend. |
| `legend_position` | `string` (`'center'`, `'left'`, `'right'`) | `Legend Align` | Legend alignment (`'center'` default). |
| `show_view_names` | `boolean` (`true`/`false`) | `Show Full Field Name` | Include LookML view prefix in labels. Default is `false`. |
| `font_size` | `string` | `Font Size` | Value label font size (e.g., `'12px'`). |
| `label_color` | `array` of `string` | `Value Colors` | Custom colors for value labels (e.g., `["#174EA6"]`). |
| `label_value_format` | `string` | `Value Format` | Explicit format string for bar value labels. |
| `label_rotation` | `number` (`-360` to `360`) | `Value Rotation` | Rotation angle in degrees for bar value labels. |
| `show_totals_labels` | `boolean` (`true`/`false`) | `Totals Labels` | Show total stack labels when `stacking: normal`. Default is `false`. |
| `totals_color` | `string` (hex color) | `Totals Color` | Color of stack total labels. Default is `'#808080'`. |
| `totals_rotation` | `number` (`-360` to `360`) | `Totals Rotation` | Rotation angle for stack total labels. |

---

## Production LookML Examples

### 1. Order Amount Percentage Distribution (`y_axis_mode: percent`, `bin_range_format: to`)
Bins `order_facts.order_amount` across up to 5,000 observations using human-readable `"x to y"` intervals and zero-gap contiguous bars:

```yaml
- title: "Order Amount Distribution (% of Orders)"
  name: order_amount_histogram
  model: thelook
  explore: order_items
  type: looker_histogram
  modern2026: true
  fields: [order_items.order_count, order_facts.order_amount]
  filters:
    order_items.months_since_signup: "[0,12]"
    users.created_month: "12 months"
  sorts: [order_items.order_count desc]
  limit: 5000
  binning_field: order_facts.order_amount
  x_axis_bin_label_format: interval
  bin_range_format: to
  x_axis_value_format: "$#,##0"
  y_axis_mode: percent
  column_spacing_ratio: 0
  column_group_spacing_ratio: 0
  show_x_axis_label: true
  x_axis_label: "Order Amount ($)"
  show_x_axis_ticks: true
  show_y_axis_labels: true
  y_axis_labels: ["Share of Orders (%)"]
  show_y_axis_ticks: true
  y_axis_scale_mode: linear
  x_axis_gridlines: false
  y_axis_gridlines: true
  show_value_labels: false
  show_view_names: false
  color_application:
    collection_id: google
    palette_id: google-categorical-0
  listen:
    State: users.state
    Country: users.country
  row: 8
  col: 0
  width: 12
  height: 8
```

### 2. Fixed-Width Customer Tenure Histogram with Pivoted Segments (`stacking: normal`)
Uses explicit `binWidth: 30` and `min: 0` across customer tenure cohorts segmented by `users.traffic_source`:

```yaml
- title: "Customer Tenure Distribution by Acquisition Channel"
  name: tenure_distribution_by_channel
  model: thelook
  explore: order_items
  type: looker_histogram
  modern2026: true
  fields: [user_order_facts.days_as_customer, users.traffic_source, users.count]
  pivots: [users.traffic_source]
  limit: 5000
  binning_field: user_order_facts.days_as_customer
  binWidth: 30
  min: 0
  bin_range_format: range
  x_axis_bin_label_format: interval
  y_axis_mode: count
  stacking: normal
  column_spacing_ratio: 0
  column_group_spacing_ratio: 0
  show_totals_labels: false
  legend_position: center
  show_view_names: false
  row: 8
  col: 12
  width: 12
  height: 8
```
