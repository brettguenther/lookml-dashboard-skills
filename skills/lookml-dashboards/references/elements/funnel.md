# LookML Dashboard Element Vis Config: Funnel and Stepped Funnel

This reference provides exact visualization configuration options for Funnel chart elements in LookML dashboards.

> [!CAUTION]
> **Looker 26.22+ Multi-Measure Funnel Rendering Defect**:
> `type: looker_funnel` strictly expects **1 dimension + 1 measure** (stage category + stage count/metric). When passed **multiple measures with 0 dimensions** (e.g., 5 sequential conversion measures), Looker silently renders **only the first metric**.
>
> **Canonical Multi-Measure Alternative**: For multi-stage conversion funnels across distinct measures, use `type: looker_column` (`modern2026: true`) with `show_dropoff: true` and `show_x_axis_ticks: false`:
>
> ```yaml
> - title: "5-Stage Digital Conversion Dropoff"
>   name: session_conversion_dropoff
>   model: thelook
>   explore: events
>   type: looker_column
>   modern2026: true
>   fields:
>     - sessions.total_visitors
>     - sessions.product_views
>     - sessions.cart_adds
>     - sessions.checkout_starts
>     - sessions.purchases
>   show_dropoff: true
>   show_x_axis_ticks: false
>   legend_position: center
>   row: 8
>   col: 0
>   width: 12
>   height: 8
> ```

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `isStepped` | `boolean (true/false)` | `Stepped Funnel` | Toggle between smooth funnel and stepped funnel |
| `labelColor` | `string` | `Label Color` | Custom hex color code for labels |
| `labelColorEnabled` | `boolean (true/false)` | `Color Label` | Enable custom label coloring |
| `labelOverlap` | `boolean (true/false)` | `Allow Label Overlap` | Toggle to allow overlapping labels |
| `labelPosition` | `string (one of: 'left', 'right', 'center', 'inline')` | `Label Position` | Position alignment for funnel step labels |
| `labelScale` | `number` | `Label Scale` | Scale multiplier for label font sizes |
| `leftAxisLabel` | `string` | `Left Axis Label` | Custom text label for left axis |
| `leftAxisLabelVisible` | `boolean (true/false)` | `Label Left Axis` | Toggle visibility of left axis label |
| `modern2026` | `boolean (set to true, otherwise omit)` | `Modern 2026 Engine` | Enable modern 2026 visualization rendering engine (default: `true`, otherwise omit) |
| `orientation` | `string (one of: 'vertical', 'horizontal')` | `Orientation` | Direction orientation of the funnel |
| `percentPosition` | `string (one of: 'inline', 'hidden', 'left', 'right')` | `Percent Position` | Position of percentage display values |
| `percentType` | `string (one of: 'prior_step', 'total')` | `Percent Type` | Calculate percentage relative to prior step or total baseline |
| `rightAxisLabel` | `string` | `Right Axis Label` | Custom text label for right axis |
| `rightAxisLabelVisible` | `boolean (true/false)` | `Label Right Axis` | Toggle visibility of right axis label |
| `smoothedBars` | `boolean (true/false)` | `Smoothed Bars` | Toggle smooth curvature on funnel bars |
| `valuePosition` | `string (one of: 'inline', 'hidden', 'left', 'right')` | `Value Position` | Position of raw value displays |
