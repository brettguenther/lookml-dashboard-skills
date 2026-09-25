# LookML Dashboard Dynamic Fields: Table Calculations, Custom Measures & Dimensions

In Looker LookML dashboards, `dynamic_fields` allows dashboard elements to define ad-hoc metrics, row-level dimension transformations, and post-query calculations directly inside the dashboard element definition without requiring updates to the underlying LookML view or model.

Looker supports three categories of `dynamic_fields`:
1. **Table Calculations** (executed in-browser over the tabular result set)
2. **Custom Dimensions** (evaluated row-by-row in SQL before aggregation)
3. **Custom Measures & Filtered Measures** (aggregated in SQL with optional filter expressions)

---

## 1. Custom Dimensions (`category: dimension`)

Custom dimensions create new dimensional attributes from existing dimensions using Looker expressions. They are executed directly in the database query's `SELECT` and `GROUP BY` clauses.

### Structure & Parameters
| Property | Type | Description |
| :--- | :--- | :--- |
| `dimension` | `string` | Unique field identifier (snake_case, no spaces). Referenced in `fields:` and `sorts:`. |
| `label` | `string` | User-facing display name. |
| `expression` | `string` | Looker dimension expression (e.g. `concat(${users.first_name}, " ", ${users.last_name})`). |
| `category` | `string` | Must be `dimension`. |
| `_kind_hint` | `string` | Set to `dimension`. |
| `_type_hint` | `string` | Data type: `string`, `number`, `date`, or `yesno`. |
| `value_format` | `string` | Optional numeric format pattern. |

### Concrete YAML Example: Custom Dimension
```yaml
- name: orders_by_customer_region
  title: "Orders by Customer Region"
  model: thelook
  explore: orders
  type: looker_column
  modern2026: true
  fields: [user_full_name, orders.count]
  sorts: [orders.count desc]
  limit: 20
  dynamic_fields:
    - dimension: user_full_name
      label: "Customer Full Name"
      expression: 'concat(${users.first_name}, " ", ${users.last_name})'
      category: dimension
      _kind_hint: dimension
      _type_hint: string
```

---

## 2. Custom Measures & Filtered Measures (`category: measure`)

Custom measures allow elements to aggregate dimensional fields or create filtered measures on the fly without modifying view files.

### Structure & Parameters
| Property | Type | Description |
| :--- | :--- | :--- |
| `measure` | `string` | Unique field identifier (snake_case, no spaces). Referenced in `fields:` and `sorts:`. |
| `label` | `string` | User-facing display name. |
| `based_on` | `string` | Field to aggregate or filter (e.g. `orders.status` or `orders.id` or `orders.count`). |
| `type` | `string` | Aggregation type: `count_distinct`, `sum`, `average`, `min`, `max`, or `count`. |
| `filter_expression` | `string` | Optional Looker boolean expression to create a filtered measure (e.g. `${orders.status} = "cancelled"`). |
| `category` | `string` | Must be `measure`. |
| `_kind_hint` | `string` | Set to `measure`. |
| `_type_hint` | `string` | Typically `number`. |
| `value_format_name` | `string` | Named format: `usd`, `usd_0`, `percent_1`, `decimal_2`, etc. |

### Concrete YAML Example: Custom Filtered Measure
```yaml
- name: order_status_breakdown
  title: "Cancelled vs Completed Revenue"
  model: thelook
  explore: order_items
  type: looker_column
  modern2026: true
  fields: [orders.created_month, cancelled_orders_count, total_cancelled_amount]
  sorts: [orders.created_month desc]
  limit: 12
  dynamic_fields:
    # Filtered Count of Cancelled Orders
    - measure: cancelled_orders_count
      label: "Cancelled Orders"
      based_on: orders.id
      type: count_distinct
      filter_expression: '${orders.status} = "cancelled"'
      category: measure
      _kind_hint: measure
      _type_hint: number

    # Filtered Sum of Sale Price for Cancelled Orders
    - measure: total_cancelled_amount
      label: "Cancelled Revenue"
      based_on: order_items.sale_price
      type: sum
      filter_expression: '${orders.status} = "cancelled"'
      value_format_name: usd_0
      category: measure
      _kind_hint: measure
      _type_hint: number
```

---

## 3. Table Calculations (`table_calculation:`)

Table calculations run in the browser after the database returns results. They are used for period-over-period comparisons, running totals, ranking, and ratios.

### Structure & Parameters
| Property | Type | Description |
| :--- | :--- | :--- |
| `table_calculation` | `string` | Unique field identifier (snake_case, no spaces). Referenced in `fields:` and `sorts:`. |
| `label` | `string` | User-facing display name. |
| `expression` | `string` | Table calculation expression using `${...}`, functions like `offset()`, `running_total()`, `index()`. |
| `value_format_name` | `string` | Named format (e.g. `percent_1`, `usd_0`). |
| `value_format` | `string` | Explicit format pattern (e.g. `"$#,##0"`). |

### Key Production Table Calculation Recipes

#### A. Period-over-Period Variance (PoP)
```yaml
- table_calculation: pop_variance
  label: "vs Prior Period"
  expression: "${orders.total_revenue} / offset(${orders.total_revenue}, 1) - 1"
  value_format_name: percent_1
```
> **Sorting Note**: To ensure `offset(..., 1)` references the earlier period, sort the date dimension in descending order (`sorts: [orders.created_month desc]`).

#### B. Cumulative Growth (Running Total)
```yaml
- table_calculation: running_arr
  label: "Cumulative ARR"
  expression: "running_total(${orders.total_revenue})"
  value_format_name: usd_0
```

#### C. Share of Total (Percentage of Column)
```yaml
- table_calculation: share_of_total
  label: "Share of Total"
  expression: "${orders.count} / sum(${orders.count})"
  value_format_name: percent_1
```

#### D. Partial Period Suppression
Prevents trend lines from plummeting to zero for an in-progress date period:
```yaml
- table_calculation: safe_trend
  label: "Completed Trend"
  expression: "if(${orders.created_date} <= now(), ${orders.count}, null)"
```

#### E. Linear Target / Goal Tracking
```yaml
- table_calculation: linear_goal
  label: "Linear Target"
  expression: "(row() / max(row())) * 50000"
  value_format_name: usd_0
```
