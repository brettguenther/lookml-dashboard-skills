# Boilerplate High-Quality LookML Dashboard

Use this template as a production-grade starting point for any new LookML dashboard. It incorporates validated modern Looker syntax, 24-column grid layout, tabbed navigation, dynamic fields (table calculations and custom measures), and proper `modern2026: true` attribution.

```yaml
- dashboard: high_quality_template
  title: "Executive Business Overview"
  description: "Executive summary and operational breakdown of performance metrics."
  preferred_viewer: dashboards-next
  style: modern
  layout: newspaper
  tile_filter_information: show_all
  query_timezone: user_timezone
  auto_run: true
  crossfilter_enabled: false

  # 1. Organization: Tabs
  tabs:
    - name: executive_summary
      label: "Executive Summary"
    - name: operational_details
      label: "Operational Details"

  # 2. Global & Tile-Scoped Filters (Notice: No periods in name identifiers)
  filters:
    - name: date_range
      title: "Date Range"
      type: date_filter
      default_value: "last 90 days"
      ui_config:
        type: relative_timeframes
        display: inline

    - name: product_category
      title: "Category"
      type: field_filter
      model: your_model
      explore: order_items
      field: products.category
      ui_config:
        type: dropdown_menu
        display: popover

    # Tile-scoped filter (vis_filter: true): popover only, required: false, bound to 1 tile
    - name: "Traffic Source - Monthly Revenue Trend"
      title: "Traffic Source"
      type: field_filter
      default_value: "Display,Email,Facebook,Organic,Search"
      allow_multiple_values: true
      required: false
      model: your_model
      explore: order_items
      listens_to_filters: []
      field: users.traffic_source
      ui_config:
        type: button_group
        display: popover
      vis_filter: true

  elements:
    # 3. Branding & Navigation Header Tile
    - name: overview_header
      type: text
      tab_name: executive_summary
      title_text: "<font color='#1F1F1F' size='4.5' weight='bold'>Business Pulse :</font> <font color='#1A73E8' size='4.5'>Overview</font>"
      body_text: |
        <div style="height: 100%; position: relative;">
          <p style="color: #5F6368; font-size: 14px;">High-level quarterly performance KPIs, trends, and regional fulfillment.</p>
        </div>
      row: 0
      col: 0
      width: 24
      height: 3

    # 4. KPI Row (Default to type: single_value - Note: single_value does NOT take modern2026)
    # Scorecard Uniformity: Keep headline numbers uniform neutral. Color is reserved for comparisons and alerts.
    - title: "Total Revenue"
      name: revenue_kpi
      model: your_model
      explore: order_items
      type: single_value
      fields: [order_items.total_sale_price, orders.created_month]
      filters:
        orders.created_date: "2 months ago for 2 months"
      sorts: [orders.created_month desc] # Descending sort ensures offset(..., 1) compares to prior month
      limit: 2
      listen:
        date_range: orders.created_date
        product_category: products.category
      dynamic_fields:
        - table_calculation: pop_change
          label: "vs Prior Month"
          expression: "${order_items.total_sale_price} / offset(${order_items.total_sale_price}, 1) - 1"
          value_format_name: percent_1
      show_comparison: true
      comparison_type: change
      comparison_label: "vs Prior Month"
      smart_single_value_size: true
      tab_name: executive_summary
      row: 3
      col: 0
      width: 8
      height: 4

    - title: "Orders Count"
      name: orders_count_kpi
      model: your_model
      explore: order_items
      type: single_value
      fields: [orders.count, orders.created_month]
      filters:
        orders.created_date: "2 months ago for 2 months"
      sorts: [orders.created_month desc]
      limit: 2
      listen:
        date_range: orders.created_date
        product_category: products.category
      dynamic_fields:
        - table_calculation: pop_orders_change
          label: "vs Prior Month"
          expression: "${orders.count} / offset(${orders.count}, 1) - 1"
          value_format_name: percent_1
      show_comparison: true
      comparison_type: change
      comparison_label: "vs Prior Month"
      smart_single_value_size: true
      tab_name: executive_summary
      row: 3
      col: 8
      width: 8
      height: 4

    # 5. KPI with Filtered Custom Measure in dynamic_fields
    - title: "Cancelled Orders"
      name: cancelled_orders_kpi
      model: your_model
      explore: order_items
      type: single_value
      fields: [cancelled_orders_count]
      listen:
        date_range: orders.created_date
        product_category: products.category
      dynamic_fields:
        - measure: cancelled_orders_count
          label: "Cancelled Orders"
          based_on: orders.id
          type: count_distinct
          filter_expression: '${orders.status} = "cancelled"'
          category: measure
          _kind_hint: measure
          _type_hint: number
      smart_single_value_size: true
      tab_name: executive_summary
      row: 3
      col: 16
      width: 8
      height: 4

    # 6. Trend Tile (modern2026: true, Monotone Interpolation & Dual Axis)
    - title: "Monthly Revenue & Orders Trend"
      name: revenue_trend
      model: your_model
      explore: order_items
      type: looker_line
      modern2026: true
      fields: [orders.created_month, order_items.total_sale_price, orders.count]
      sorts: [orders.created_month asc]
      limit: 500
      interpolation: monotone
      point_style: circle_outline
      x_axis_label_rotation: -45
      y_axes:
        - label: "Revenue"
          orientation: left
          series:
            - id: order_items.total_sale_price
              name: "Total Sale Price"
        - label: "Orders Count"
          orientation: right
          series:
            - id: orders.count
              name: "Orders Count"
      listen:
        date_range: orders.created_date
        product_category: products.category
        Traffic Source - Monthly Revenue Trend: users.traffic_source
      tab_name: executive_summary
      row: 7
      col: 0
      width: 24
      height: 8

    # 7. Map Tile (Always default to looker_google_map - Note: does NOT take modern2026)
    - title: "Regional Store Performance"
      name: regional_store_map
      model: your_model
      explore: order_items
      type: looker_google_map
      fields: [distribution_centers.location, distribution_centers.name, orders.count]
      filters:
        distribution_centers.location: "-NULL"
      sorts: [orders.count desc]
      limit: 500
      map_tile_provider: light
      map_position: fit_data
      map_marker_type: circle
      map_marker_radius_mode: proportional_value
      map_marker_radius_min: 3
      map_marker_radius_max: 18
      map_marker_units: pixels
      map_marker_color_mode: value
      map_value_colors: ["#E8F0FE", "#4285F4", "#1967D2", "#0D47A1"]
      show_legend: true
      show_view_names: false
      listen:
        date_range: orders.created_date
        product_category: products.category
      tab_name: executive_summary
      row: 15
      col: 0
      width: 24
      height: 9

    # 8. Operational Details Tab: Bullet SLA Goal & Order Amount Histogram (Reset row: 0 for new tab)
    - title: "Days to Process SLA by Distribution Center"
      name: days_to_process_bullet
      model: your_model
      explore: order_items
      type: looker_bullet
      modern2026: true
      fields: [distribution_centers.name, order_items.average_days_to_process]
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
      bullet_show_target_marker: true
      bullet_target_type: value
      bullet_target: 4
      bullet_target_color: "#E8710A"
      bullet_target_width: "120%"
      bullet_target_height: 5
      listen:
        date_range: orders.created_date
        product_category: products.category
      tab_name: operational_details
      row: 0
      col: 0
      width: 12
      height: 8

    - title: "Order Amount Distribution (% Share)"
      name: order_amount_histogram
      model: your_model
      explore: order_items
      type: looker_histogram
      modern2026: true
      fields: [order_items.order_count, order_items.sale_price]
      sorts: [order_items.order_count desc]
      limit: 5000
      binning_field: order_items.sale_price
      x_axis_bin_label_format: interval
      bin_range_format: to
      y_axis_mode: percent
      column_spacing_ratio: 0
      column_group_spacing_ratio: 0
      listen:
        date_range: orders.created_date
        product_category: products.category
      tab_name: operational_details
      row: 0
      col: 12
      width: 12
      height: 8

    # 9. Operational Details Tab Grid
    - title: "Product Category Breakdown"
      name: product_category_grid
      model: your_model
      explore: order_items
      type: looker_grid
      modern2026: true
      fields: [products.category, products.brand, orders.count, order_items.total_sale_price]
      sorts: [order_items.total_sale_price desc]
      limit: 100
      show_totals: true
      size_to_fit: true
      series_cell_visualizations:
        order_items.total_sale_price:
          is_active: true
      listen:
        date_range: orders.created_date
        product_category: products.category
      tab_name: operational_details
      row: 8
      col: 0
      width: 24
      height: 12
```
