# LookML Dashboard Skills

Production-grade LookML dashboard design and implementation skills for AI coding agents (Gemini Antigravity, Claude, Cursor, CodeMind, etc.).

## Features

- **`lookml-dashboards`**: Unified skill covering dashboard layout (`newspaper` 24-column grid), sectioning, tabs, KPI comparison best practices, dynamic fields/table calculations, mixed series and dual axes, dashboard filters (`ui_config`), advanced markdown/HTML styling, embedding, and performance optimization.
- **Element Visualization References**: Exhaustive parameter references for 10 Looker visualization types nested under `references/elements/`:
  - Cartesian (Line, Bar, Column, Area, Scatter, Waterfall)
  - Conditional Formatting Syntax
  - Funnel & Stepped Funnel
  - KPI (Key Performance Indicator)
  - Maps (Google Maps, Mapbox)
  - Single Value
  - Single Record
  - Table & Grid
  - Timeline
  - Word Cloud

## Quick Start (Installation via `npx`)

In your LookML repository or agent workspace, run:

```bash
npx github:brettguenther/lookml-dashboard-skills
```

The installer will automatically detect your project's agent framework directory (`.agents/skills`, `.gemini/skills`, `.cursor/skills`, or `.claude/skills`) and install the skill.

## License

MIT
