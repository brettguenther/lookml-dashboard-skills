# LookML Dashboard Element Vis Config: Table and Grid

This reference provides exact visualization configuration options for Table and Grid elements in LookML dashboards.

## Options Reference Table

| Option Key / Path | Type | Label | Description |
| :--- | :--- | :--- | :--- |
| `conditional_formatting_include_nulls` | `boolean (true/false)` | `Include Null Values as Zero` | Include null values as zero in conditional formatting calculations |
| `conditional_formatting_include_totals` | `boolean (true/false)` | `Include Totals` | Include summary totals rows in conditional formatting rules |
| `enable_conditional_formatting` | `boolean (true/false)` | `Enable Conditional Formatting` | Toggle conditional formatting rules |
| `header_background_color` | `string` | `Header Background Color` | Hex color code for table header background |
| `header_font_color` | `string` | `Header Font Color` | Hex color code for table header text |
| `header_font_size` | `number (pixels, e.g. 12)` | `Header Font Size` | Font size in pixels for header row (do NOT pass string keywords like 'medium') |
| `header_text_alignment` | `string (one of: 'left', 'center', 'right')` | `Header Alignment` | Text alignment for header text |
| `minimum_column_width` | `number` | `Minimum Column Width` | Minimum width in pixels for table columns |
| `modern2026` | `boolean (set to true, otherwise omit)` | `Modern 2026 Engine` | Enable modern 2026 visualization rendering engine (default: `true`, otherwise omit) |
| `row_groups.enabled` | `boolean (true/false)` | `Enable Row Groups` | Enable collapsible row grouping hierarchy |
| `row_groups.row_grouping_fields` | `list of strings` | `Grouped Dimensions` | Ordered list of dimension field names to group into the tree hierarchy column |
| `row_groups.default_display_level` | `string (one of: 'collapsed', 'top_expanded', 'all_expanded')` | `Default Display Level` | Initial expansion depth of grouped tree rows |
| `row_groups.group_column_header` | `string` | `Group Column Header` | Custom column header label for the auto-generated tree hierarchy column |
| `row_groups.show_group_counts` | `boolean (true/false)` | `Show Group Counts` | Display count of child rows within each group, e.g. `(N)` |
| `row_groups.configurable_subtotals` | `boolean (true/false)` | `Show Subtotal Row` | Display client-side subtotal rollup rows for `sum` and `count` measures |
| `row_groups.subtotal_location` | `string (one of: 'bottom', 'top')` | `Subtotal Location` | Render subtotals at top or bottom of group |
| `row_groups.show_grouped_columns` | `boolean (true/false)` | `Show Grouped Columns` | If false, hides standalone grouped dimension columns and merges them into tree column |
| `rows_font_size` | `number (pixels, e.g. 12)` | `Rows Font Size` | Font size in pixels for data rows (do NOT pass string keywords like 'medium') |
| `series_cell_visualizations.<field_name>.is_active` | `boolean (true/false)` | `Cell Visualization` | Toggle in-cell bar/bullet visualization for numeric field |
| `series_cell_visualizations.<field_name>.value_display` | `boolean (true/false)` | `Show Value Display` | Show numeric value display alongside cell bar visualization |
| `series_cell_visualizations.<field_name>.value_labels` | `boolean (true/false)` | `Show Value Labels` | Show numeric value labels alongside cell bar visualization |
| `series_column_widths.<field_name>` | `number` | `Width` | Custom width in pixels for specific column |
| `series_labels.<field_name>` | `string` | `Label` | Custom column header text override |
| `series_text_format.<field_name>.align` | `string (one of: 'left', 'center', 'right')` | `Alignment` | Text alignment for specific column (or grouped dimension hierarchy level) |
| `series_text_format.<field_name>.bg_color` | `string` | `Background Color` | Custom background color for specific column (or grouped dimension hierarchy level) |
| `series_text_format.<field_name>.fg_color` | `string` | `Foreground Color` | Custom text font color for specific column (or grouped dimension hierarchy level) |
| `series_text_format.<field_name>.bold` | `boolean (true/false)` | `Bold` | Bold text styling for specific column (or grouped dimension hierarchy level) |
| `series_text_format.<field_name>.italic` | `boolean (true/false)` | `Italic` | Italic text styling for specific column (or grouped dimension hierarchy level) |
| `series_value_format.<field_name>` | `string` | `Value Format` | Numeric format pattern string for specific column |
| `show_row_numbers` | `boolean (true/false)` | `Show Row Numbers` | Display row index numbers on left edge (automatically hidden if `row_groups.enabled: true`) |
| `show_row_totals` | `boolean (true/false)` | `Show Row Totals` | Display horizontal row total calculations |
| `show_totals` | `boolean (true/false)` | `Show Totals` | Display vertical column summary total calculations |
| `show_view_names` | `boolean (true/false)` | `Show Full Field Name` | Show full view and field name in column headers |
| `size_to_fit` | `boolean (true/false)` | `Size Columns to Fit` | Auto-stretch columns to fill table container width |
| `table_column_groups.enabled` | `boolean (true/false)` | `Enable Column Groups` | Enable multi-column banner grouping headers |
| `table_column_groups.defaultDisplayState` | `string ('expanded', 'collapsed')` | `Default Display State`| Initial display state of all column groups |
| `table_column_groups.namespaceCsvHeaders` | `boolean (true/false)` | `Namespace CSV Headers`| Prepend group title to column names when exporting to CSV |
| `table_column_groups.groups` | `list of objects` | `Column Groups List` | Up to 20 group definitions (see below for group object schema) |
| `table_column_hover_highlight_enable` | `boolean (true/false)` | `Enable Hover Highlighting` | Highlight row/column on mouse hover |
| `table_custom_border_color` | `string` | `Border Color` | Hex color code for cell grid borders |
| `table_custom_border_enable` | `boolean (true/false)` | `Custom Borders` | Enable custom border styling |
| `table_custom_border_style` | `string (one of: 'solid', 'dashed', 'dotted')` | `Border Style` | Line style of table borders |
| `table_custom_border_width` | `number` | `Border Width` | Width in pixels of table borders |
| `table_enable_pagination` | `boolean (true/false)` | `Enable Pagination` | Enable paged table navigation |
| `table_page_size_options` | `string` | `Page Size Options` | Comma-separated page size choices (e.g. `"10,25,50"`) |
| `table_show_footer` | `boolean (true/false)` | `Show Footer` | Display table footer bar |
| `table_show_headers` | `boolean (true/false)` | `Show Headers` | Show or hide table header row |
| `table_theme` | `string (one of: 'modern', 'white', 'transparent', 'editable', 'gray', 'unstyled')` | `Table Theme` | Pre-styled theme palette for table |
| `transpose` | `boolean (true/false)` | `Transpose` | Swap rows and columns |
| `truncate_header` | `boolean (true/false)` | `Truncate Column Names` | Truncate long column names with ellipsis |
| `truncate_text` | `boolean (true/false)` | `Truncate Text` | Truncate long cell text values with ellipsis |

---

## 2. Row Groups Hierarchy (`row_groups`)

Enables collapsible parent-child tree hierarchy grouping inside modern `looker_grid` / `table` visualizations (`modern2026: true`).

### Mutual Exclusivity & Aggregation Rules

1. **Pagination Incompatibility**: `row_groups.enabled: true` is **mutually exclusive with `table_enable_pagination: true`**. If pagination is active, the grid disables row grouping.
2. **Sparklines Incompatibility**: `row_groups.enabled: true` is **mutually exclusive with `table_sparklines.enabled: true`**.
3. **Subtotal Rollup Limitation**: When `row_groups.configurable_subtotals: true`, AG Grid computes client-side subtotals **only for `sum` and `count` measures**. Averages, distinct counts, minimums, maximums, and table calculations render blank on group header rows to prevent mathematically invalid rollups.
4. **Per-Tier Styling**: Applying `series_text_format.<dimension_name>` to any grouped dimension in `row_grouping_fields` styles **that exact hierarchy depth level** inside the auto-column tree.

```yaml
row_groups:
  enabled: true
  row_grouping_fields:
    - products.department             # Level 0 (outermost tree parent)
    - products.category               # Level 1 (nested child)
  default_display_level: all_expanded # 'collapsed' | 'top_expanded' | 'all_expanded'
  group_column_header: "Merchandising Hierarchy"
  show_group_counts: true             # Displays child count '(N)' next to parent label
  configurable_subtotals: true        # Enables rollup subtotals on sum/count measures
  subtotal_location: bottom           # 'bottom' | 'top'
  show_grouped_columns: false         # Hides standalone columns for grouped dimensions
```

---

## 3. Collapsible Column Groups (`table_column_groups`)

Creates multi-tier banner headers spanning multiple related measure or dimension columns.

### Mutual Exclusivity Rules

1. **Pivot Incompatibility**: Column groups are **disabled when queries contain `pivots`**.
2. **Transpose Incompatibility**: Column groups are **disabled when `transpose: true`**.
3. **Capacity Limits**: Maximum 20 groups per table (`MAX_COLUMN_GROUPS`), maximum 50 columns per group (`MAX_COLUMNS_PER_GROUP`).

```yaml
table_column_groups:
  enabled: true
  defaultDisplayState: expanded       # 'expanded' | 'collapsed'
  namespaceCsvHeaders: true           # Prefixes exported CSV headers with group title
  groups:
    - id: fulfillment_volume
      title: "Fulfillment & Volume"
      columns:
        - order_items.status
        - order_items.count
      defaultDisplayState: expanded
      collapsedVisibleColumns:        # Column that stays visible when group is collapsed
        - order_items.count
      headerBackgroundColor: "#1a73e8"
      headerTextColor: "#ffffff"
    - id: financial_performance
      title: "Financial Performance"
      columns:
        - order_items.total_sale_price
        - inventory_items.total_cost
        - order_items.average_sale_price
      defaultDisplayState: expanded
      collapsedVisibleColumns:
        - order_items.total_sale_price
      headerBackgroundColor: "#137333"
      headerTextColor: "#ffffff"
```

---

## 4. Complete LookML Table Example

```yaml
- name: merchandising_hierarchy_table
  title: "Merchandising Hierarchy & Fulfillment Performance"
  model: thelook
  explore: order_items
  type: looker_grid
  fields:
    - products.department
    - products.category
    - order_items.status
    - order_items.count
    - order_items.total_sale_price
    - inventory_items.total_cost
    - order_items.average_sale_price
  sorts:
    - products.department asc
    - order_items.total_sale_price desc
  limit: 50
  modern2026: true
  show_view_names: false
  show_row_numbers: false
  size_to_fit: true
  header_font_size: 12                # Integer pixels, NOT string
  rows_font_size: 12                  # Integer pixels, NOT string
  row_groups:
    enabled: true
    row_grouping_fields:
      - products.department
      - products.category
    default_display_level: all_expanded
    group_column_header: "Department › Category"
    show_group_counts: true
    configurable_subtotals: true
    show_grouped_columns: false
  table_column_groups:
    enabled: true
    defaultDisplayState: expanded
    namespaceCsvHeaders: true
    groups:
      - id: fulfillment_volume
        title: "Fulfillment & Volume"
        columns:
          - order_items.status
          - order_items.count
        defaultDisplayState: expanded
        collapsedVisibleColumns:
          - order_items.count
        headerBackgroundColor: "#1a73e8"
        headerTextColor: "#ffffff"
      - id: financials
        title: "Financial Metrics"
        columns:
          - order_items.total_sale_price
          - inventory_items.total_cost
          - order_items.average_sale_price
        defaultDisplayState: expanded
        collapsedVisibleColumns:
          - order_items.total_sale_price
        headerBackgroundColor: "#137333"
        headerTextColor: "#ffffff"
  series_text_format:
    products.department:
      bold: true
      fg_color: "#174ea6"
      bg_color: "#e8f0fe"
    products.category:
      bold: true
      fg_color: "#0d652d"
      bg_color: "#e6f4ea"
  series_cell_visualizations:
    order_items.total_sale_price:
      is_active: true
```

---

## 5. `modern2026: true` Rendering Gotchas & Pivoted Cell Bars

1. **String Font Sizes Cause Blank Tables (`NaN` Row Height)**:
   - Never pass string keywords (`"small"`, `"medium"`, `"large"`) to `rows_font_size` or `header_font_size` on `looker_grid` with `modern2026: true`. Looker's virtualized table layout computes `NaN` (`0px`) row heights and renders a completely blank table body. Always pass numeric pixel integers (`header_font_size: 11`, `rows_font_size: 12`) or omit them.
2. **Suppressing Unwanted Default Cell Bars on the First Measure**:
   - Looker automatically enables `series_cell_visualizations` (`is_active: true`) on the first visible measure of every `looker_grid`. Explicitly set `is_active: false` on the first measure when cell bars are not desired on that column.
3. **Pivoted `looker_grid` Cell-Bar Squishing (`_kind_hint: supermeasure`)**:
   - Enabling `series_cell_visualizations` on a pivoted measure squishes inline cell bars to `1px` ticks. Keep pivoted measures as plain numeric columns (`is_active: false`) and add an unpivoted `_kind_hint: supermeasure` table calculation (`coalesce(pivot_where(${dim} = "Value", ${measure}), 0)`) to render full-width inline cell bars.
