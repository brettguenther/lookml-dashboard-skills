# LookML Dashboard Skills

Production-grade LookML dashboard design, implementation, and rendering validation skills.

> [!IMPORTANT]
> **Looker Preview Visualization Features Prerequisite**: This skill is built to take full advantage of all preview visualization and dashboard features available in Looker — including the **Modern 2026 Visualization Engine** (`modern2026: true`), **Filters on Tiles** (`vis_filter: true`, `tile_filter_information`), **Granular 72-Column Newspaper Grids** (`layout_granularity: granular`), **Dashboard Tile Groups** (`type: group`), **Table Hierarchy Row & Column Grouping** (`row_groups`, `table_column_groups`), **Bullet Charts** (`looker_bullet`), and **Histograms** (`looker_histogram`). The expectation is that these preview features have been enabled in your Looker environment (under **Admin → Labs / Platform**).

## Features

- **`lookml-dashboards`**: Unified skill covering dashboard layout (`newspaper` 24-column default and 72-column `layout_granularity: granular` grids), sectioning, isolated tab coordinate grids, dashboard tile groups (`type: group`), KPI scorecard design (defaulting to `type: single_value`), dynamic fields (table calculations, custom dimensions, and custom measures), mixed series and dual axes, global and tile-scoped dashboard filters (`ui_config`, `vis_filter: true`), table hierarchy grouping (`row_groups`, `table_column_groups`), advanced markdown/HTML styling, and performance optimization.
- **Dynamic Fields Coverage**: Full syntax and production patterns for:
  - Table Calculations (`table_calculation:`)
  - Custom Dimensions (`category: dimension`, `expression:`)
  - Custom Filtered Measures (`category: measure`, `based_on:`, `type:`, `filter_expression:`)
- **Element Visualization References**: Exhaustive parameter references for Looker visualization types nested under `references/elements/`:
  - Single Value (`single_value`) _(Default for all KPIs and summary metrics)_
  - Bullet Chart (`looker_bullet`) _(Actual vs target goal & qualitative threshold bands)_
  - Histogram (`looker_histogram`) _(Continuous frequency / percent bucket distributions)_
  - Google Maps (`looker_google_map`) _(Default for all maps, plus `looker_geo_choropleth` custom GeoJSON/TopoJSON rules)_
  - Cartesian (`looker_column`, `looker_bar`, `looker_line`, `looker_area`, `looker_scatter`, `looker_waterfall`, `looker_boxplot`, `looker_histogram`)
  - Table & Grid (`looker_grid`, `table`) _(Including `row_groups`, `table_column_groups`, and `modern2026: true` rendering rules)_
  - Conditional Formatting Syntax
  - Funnel & Stepped Funnel (`looker_funnel`)
  - Timeline (`looker_timeline`)
  - Word Cloud (`looker_wordcloud`)
  - Single Record (`looker_single_record`) _(Used only when explicitly requested)_
- **Rendering & Compiler Validator**: Simple, non-stylistic validator script checking only conditions expected to break rendering or compilation:
  - `modern2026: true` present on all supporting visualizations (including `looker_bullet` and `looker_histogram`) and omitted on unsupported ones (`single_value`, `looker_single_record`, `type: group`, maps)
  - No periods (`.`) in element or filter `name` identifiers
  - `y_axes[*].series` formatted as objects with `id` (`{id: ...}`), never raw strings
  - Numeric pixel integers (`11`, `12`) for `rows_font_size` / `header_font_size` on `modern2026: true` grids (rejecting strings like `'small'` that cause `NaN` `0px` blank tables)
  - `crossfilter_enabled: false` enforcement when dashboard tiles span multiple Explores
  - `single_value` `comparison_row` string enum (`first | second | last | total`) and descending-sort PoP validation
  - Tab assignment integrity

## Quick Start (Installation & Validation via `npx`)

### 1. Install Skills into Workspace

In your LookML repository or agent workspace, run:

```bash
npx github:brettguenther/lookml-dashboard-skills
```

The installer will automatically detect your project's agent framework directory (`.agents/skills`, `.gemini/skills`, `.cursor/skills`, or `.claude/skills`) and install the skill. You can also specify a custom target directory:

```bash
npx github:brettguenther/lookml-dashboard-skills --target .gemini/skills
```

### 2. Validate LookML Dashboards

Validate dashboard LookML files for fatal rendering bugs:

```bash
npx github:brettguenther/lookml-dashboard-skills --validate path/to/dashboards/
# or directly with python:
python3 scripts/validate_dashboard.py path/to/dashboards/
```

## License

MIT
