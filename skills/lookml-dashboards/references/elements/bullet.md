# LookML Dashboard Element Vis Config: Bullet Chart (`looker_bullet`)

Bullet charts (`type: looker_bullet`) compare a primary metric value (**Actual**) against a goal marker (**Target**) overlaid on qualitative background range bands (e.g., Poor / Satisfactory / Excellent).

> [!IMPORTANT]
> - **Modern Engine Required**: Always include `modern2026: true` on `looker_bullet` elements (activates modern bar fill `#174EA6` and qualitative band defaults `["#669DF6", "#8AB4F8", "#AECBFA"]` unless overridden).
> - **Query Shape Validation (`validateBullet`)**:
>   - **Dimensions**: `0` (single summary bullet) or `1` (categorical multi-bullet series, e.g., `distribution_centers.name`). More than `1` dimension fails validation (`"Bullet chart supports at most 1 dimension."`).
>   - **Measures**: At least `1` numeric measure (`measures[0]` renders as the **Actual** bar). A 2nd measure or numeric `dynamic_fields` table calculation can optionally drive dynamic per-row targets (`bullet_target_type: metric`).
>   - **Pivots**: **Strictly unsupported (`0` pivots)** (`"Pivots are not supported"`).
>   - **Row Limit**: Up to `50` data rows (`MAX_BULLET_DATA_ROWS = 50`).
> - **Clean LookML Hygiene**: Do **not** include stale Cartesian properties (`interpolation`, `point_style`, `trellis`, `stacking`, or mismatched `y_axes[*].series` entries left over from changing chart types in the Looker UI).

---

## Options Reference Table (`type: looker_bullet`)

### Plot, Ranges & Target Marker Options

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `modern2026` | `boolean` (`true`) | `Visualization Theme` | Enable Modern 2026 visualization styling engine. **Recommended: `true`**. |
| `bullet_orientation` | `string` (`'horizontal'`, `'vertical'`) | `Orientation` | Axis orientation of bullet bars. Default is `'horizontal'`; use `'vertical'` for side-by-side column-style bullets. |
| `show_legend` | `boolean` (`true`/`false`) | `Show Legend` | Toggle visibility of the chart legend. Default is `false`. |
| `bullet_range_limits_enabled` | `boolean` (`true`/`false`) | `Show Ranges` | Display qualitative background threshold bands (`Range 1`, `Range 2`, `Range 3`). Default is `true`. |
| `bullet_range_type` | `string` (`'value'`, `'metric'`) | `Range Type` | Threshold mode for qualitative bands. Use `'value'` for explicit numeric thresholds (`bullet_range_1..3`). |
| `bullet_range_1` | `number` | `Range 1` | Upper numeric threshold for qualitative Band 1 (`0` to `bullet_range_1`). Dynamic fallback: `0.75 * max`. |
| `bullet_range_2` | `number` | `Range 2` | Upper numeric threshold for qualitative Band 2 (`bullet_range_1` to `bullet_range_2`). Dynamic fallback: `1.0 * max`. |
| `bullet_range_3` | `number` | `Range 3` | Upper numeric threshold for qualitative Band 3 (`bullet_range_2` to `bullet_range_3`). Dynamic fallback: `1.25 * max`. |
| `bullet_ranges` | `string` | `Qualitative Range Thresholds` | Legacy/fallback comma-separated ascending numeric thresholds (e.g., `'0,50,100'`; max 10 bands, `<= 255` chars) used when `bullet_range_limits_enabled` is omitted. |
| `bullet_show_target_marker` | `boolean` (`true`/`false`) | `Show Target Marker` | Render the crossbar target marker line on each bullet bar. Default is `true`. |
| `bullet_target_type` | `string` (`'value'`, `'metric'`) | `Target Type` | Target source mode: `'value'` uses static `bullet_target`; `'metric'` binds per-row values from `bullet_target_metric` (defaults to `'metric'` when >=2 measures/table calcs exist, otherwise `'value'`). |
| `bullet_target` | `number` | `Target Value` | Static numeric target threshold rendered across all bars when `bullet_target_type: value` (e.g., `4`). |
| `bullet_target_metric` | `string` | `Target Measure` | Field or table calculation identifier (`view.measure_name` or `calc_name`) supplying per-row targets when `bullet_target_type: metric`. |
| `bullet_target_color` | `string` (hex color) | `Target Marker Color` | Hex color code for the target crossbar marker. Default is `'#333333'` (e.g., `'#E8710A'` for high contrast). |
| `bullet_target_width` | `string` | `Target Width` | Width of the target crossbar relative to bar width. Default is `'140%'` (e.g., `'120%'` or `'140%'`). |
| `bullet_target_height` | `number` (`1` to `20`) | `Target Thickness` | Pixel thickness of the target marker line. Default is `3` (e.g., `5`). |

### Series, Value Labels & Axes Options

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `color_application` | `object` | `Color Configuration` | Color collection and palette config (`collection_id`, `palette_id`, `options.steps`, `options.reverse`). |
| `series_colors` | `object` (`map`) | `Series Colors` | Custom bar color keyed by primary measure name or label (e.g., `{ order_items.average_days_to_process: "#1A73E8" }`). |
| `bullet_range_colors` | `array` of `string` | `Range Band Colors` | Background hex colors for qualitative bands (e.g., `["#669DF6", "#8AB4F8", "#AECBFA"]` or `["#DADCE0", "#BDC1C6", "#9AA0A6"]`). |
| `bullet_blend_colors` | `boolean` (`true`/`false`) | `Blend Range Colors` | Render qualitative thresholds as a smooth linear gradient instead of discrete stepped bands. Default is `false`. |
| `bullet_show_labels` | `boolean` (`true`/`false`) | `Label Values` | Display data value labels on the primary bullet bar. Default is `false` *(note: use `bullet_show_labels`, not `show_value_labels`)*. |
| `bullet_label_font_family` | `string` | `Label Font Family` | Font family for bullet value labels (default `'Arial, sans-serif'`). |
| `bullet_label_font_size` | `number` (`1` to `99`) | `Label Font Size` | Font size in pixels for bullet value labels. Default is `11`. |
| `bullet_label_font_color` | `string` (hex color) | `Label Font Color` | Custom hex color for bullet value labels (defaults to the primary bar color). |
| `show_x_axis_label` | `boolean` (`true`/`false`) | `Show Axis Name` | Toggle category axis title visibility. Default is `false`. |
| `x_axis_label` | `string` | `Custom Axis Name` | Custom text override for category axis title. |
| `show_x_axis_ticks` | `boolean` (`true`/`false`) | `Show Axis Value Labels` | Toggle category tick labels. Default is `true`. |
| `x_axis_label_rotation` | `number` (`-360` to `360`) | `Label Rotation` | Rotation angle in degrees for category labels (e.g., `-45`). |
| `x_axis_gridlines` | `boolean` (`true`/`false`) | `Show Gridlines` | Toggle gridlines along the category axis. Default is `false`. |
| `x_axis_reversed` | `boolean` (`true`/`false`) | `Reverse Axis` | Reverse category sort order along X-axis. Default is `false`. |
| `x_axis_zoom` | `boolean` (`true`/`false`) | `Allow Zoom` | Enable interactive zoom along category axis. Default is `true`. |
| `x_padding_left` / `x_padding_right` | `number` (`0` to `100`) | `Padding Left / Right` | Horizontal plot padding in integer units (`0`–`100`). |
| `y_axis_gridlines` | `boolean` (`true`/`false`) | `Show Gridlines` | Toggle gridlines along the quantitative value axis. Default is `false`. |
| `y_axis_reversed` | `boolean` (`true`/`false`) | `Reverse Axis` | Reverse quantitative axis direction. Default is `false`. |
| `y_axis_zoom` | `boolean` (`true`/`false`) | `Allow Zoom` | Enable interactive zoom along value axis (requires `x_axis_zoom: true`). Default is `true`. |
| `y_axes` | `array` of `object` | `Y Axis Configuration` | Optional single-axis configuration list: `[{ label, type: 'linear'|'log', showLabels, showValues, valueFormat, minValue, maxValue, unpinAxis, tickDensity: 'default'|'custom', tickDensityCustom }]`. |
| `global_tooltip_options` | `object` | `Custom Tooltip Options` | Optional custom HTML/style tooltip configuration (`enable_custom_tooltip: true`). |

---

## Production LookML Examples

### 1. Vertical Categorical Bullet Chart with Static SLA Target & Qualitative Bands
Compares processing SLA days across distribution centers (`1 dimension + 1 measure`) against a static 4-day SLA target marker (`bullet_target: 4`) and explicit qualitative thresholds (`1`, `3`, `5`):

```yaml
- title: "Days to Process by Distribution Center"
  name: days_to_process_bullet
  model: thelook
  explore: order_items
  type: looker_bullet
  modern2026: true
  fields: [distribution_centers.name, order_items.average_days_to_process]
  filters:
    order_items.months_since_signup: "[0,12]"
    users.created_month: "12 months"
  sorts: [order_items.average_days_to_process desc]
  limit: 20
  bullet_orientation: vertical
  show_legend: false
  bullet_range_limits_enabled: true
  bullet_range_type: value
  bullet_range_1: 1
  bullet_range_2: 3
  bullet_range_3: 5
  bullet_range_colors: ["#DADCE0", "#BDC1C6", "#9AA0A6"]
  bullet_blend_colors: false
  bullet_show_target_marker: true
  bullet_target_type: value
  bullet_target: 4
  bullet_target_color: "#E8710A"
  bullet_target_width: "120%"
  bullet_target_height: 5
  bullet_show_labels: true
  bullet_label_font_size: 11
  color_application:
    collection_id: google
    palette_id: google-categorical-0
  series_colors:
    order_items.average_days_to_process: "#174EA6"
  show_x_axis_label: false
  show_x_axis_ticks: true
  x_axis_gridlines: false
  y_axis_gridlines: false
  listen:
    State: users.state
    Country: users.country
  row: 0
  col: 12
  width: 12
  height: 8
```

### 2. Horizontal Goal Attainment Bullet Chart with Dynamic Measure Target (`bullet_target_type: metric`)
Uses a second query measure (`sales_targets.quota_amount`) so each regional bar renders its own dynamic quota marker:

```yaml
- title: "Regional Revenue vs Quota Attainment"
  name: regional_quota_bullet
  model: thelook
  explore: order_items
  type: looker_bullet
  modern2026: true
  fields: [users.region, order_items.total_sale_price, sales_targets.quota_amount]
  sorts: [order_items.total_sale_price desc]
  limit: 10
  bullet_orientation: horizontal
  show_legend: true
  bullet_range_limits_enabled: true
  bullet_range_type: value
  bullet_range_colors: ["#669DF6", "#8AB4F8", "#AECBFA"]
  bullet_show_target_marker: true
  bullet_target_type: metric
  bullet_target_metric: sales_targets.quota_amount
  bullet_target_color: "#EA4335"
  bullet_target_width: "140%"
  bullet_target_height: 4
  bullet_show_labels: true
  y_axes:
    - label: "Revenue ($)"
      type: linear
      showLabels: true
      showValues: true
      valueFormat: "$#,##0"
  row: 8
  col: 0
  width: 12
  height: 8
```
