# LookML Dashboard Element Vis Config: Funnel and Stepped Funnel

This reference provides exact visualization configuration options for Funnel chart elements in LookML dashboards.

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
