# LookML Dashboard Element Vis Config: KPI / Single Value

In Looker dashboards, KPI scorecard tiles are built using `type: single_value`.

> [!NOTE]
> For the comprehensive parameter reference, comparison calculation methods, and production YAML templates, refer directly to [Single Value Parameter Reference](single_value.md).
> 
> Remember:
> - **Always default to `type: single_value`** for KPIs and scorecard metrics.
> - `type: looker_single_record` (or `single_record`) is for single-row record inspection only, and should only be used when explicitly requested.
> - Single value elements do **NOT** take `modern2026: true`.
