# LookML Dashboard Skills

Production-grade LookML dashboard design, implementation, and rendering validation skills.

## Features

- **`lookml-dashboards`**: Unified skill covering dashboard layout (`newspaper` 24-column grid), sectioning, isolated tab coordinate grids, KPI scorecard design (defaulting to `type: single_value`), dynamic fields (table calculations, custom dimensions, and custom measures), mixed series and dual axes, dashboard filters (`ui_config`), advanced markdown/HTML styling, and performance optimization.
- **Dynamic Fields Coverage**: Full syntax and production patterns for:
  - Table Calculations (`table_calculation:`)
  - Custom Dimensions (`category: dimension`, `expression:`)
  - Custom Filtered Measures (`category: measure`, `based_on:`, `type:`, `filter_expression:`)
- **Element Visualization References**: Exhaustive parameter references for Looker visualization types nested under `references/elements/`:
  - Single Value (`single_value`) _(Default for all KPIs and summary metrics)_
  - Google Maps (`looker_google_map`) _(Default for all maps, with full parameter reference)_
  - Cartesian (`looker_column`, `looker_bar`, `looker_line`, `looker_area`, `looker_scatter`, `looker_waterfall`, `looker_boxplot`, `looker_histogram`)
  - Table & Grid (`looker_grid`, `table`)
  - Conditional Formatting Syntax
  - Funnel & Stepped Funnel (`looker_funnel`)
  - Timeline (`looker_timeline`)
  - Word Cloud (`looker_wordcloud`)
  - Single Record (`looker_single_record`) _(Used only when explicitly requested)_
- **Rendering & Compiler Validator**: Simple, non-stylistic validator script checking only conditions expected to break rendering or compilation:
  - `modern2026: true` present on all supporting visualizations and omitted on unsupported ones (`single_value`, `looker_single_record`, maps)
  - No periods (`.`) in element or filter `name` identifiers
  - `y_axes[*].series` formatted as objects with `id` (`{id: ...}`), never raw strings
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
