# LookML Dashboard Element Vis Config: Google Maps (`looker_google_map`)

In Looker dashboards, **always default to `type: looker_google_map`** for geographic and geospatial visualizations.

> [!IMPORTANT]
> - **Primary Map Type**: `type: looker_google_map` is the canonical, interactive vector map engine powered by Google Maps Platform.
> - **Legacy / Static Maps**: `looker_geo_choropleth` (static TopoJSON regions) and `looker_geo_coordinates` (static point plots) render static image-like assets and should **only be used if explicitly requested**.
> - **Engine Flag**: Map visualization elements (`looker_google_map`, `looker_geo_choropleth`, `looker_geo_coordinates`) do **not** use `modern2026: true`. Omit this flag from map elements.

---

## Options Reference Table (`looker_google_map`)

### 1. Plot Mode & Geometry (`map_plot_mode`)
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_plot_mode` | `string` (`'points'`, `'automagic_heatmap'`, `'heatmap'`, `'3d_heatmap'`, `'lines'`, `'areas'`) | Visualization geometry. Default is `'points'`. `'automagic_heatmap'` auto-aggregates query points. `'3d_heatmap'` produces extruded 3D hex bins. |

### 2. Map Background & Positioning
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_tile_provider` | `string` (`'light'`, `'light_no_labels'`, `'dark'`, `'dark_no_labels'`, `'satellite'`, `'satellite_streets'`, `'streets'`, `'outdoors'`, `'traffic_day'`, `'traffic_night'`, `'minimal'`) | Map canvas styling theme. Default is `'light'`. |
| `map_position` | `string` (`'fit_data'`, `'custom'`) | Positioning strategy. `'fit_data'` automatically centers and fits all query coordinates. `'custom'` uses explicit center/zoom. |
| `map_latitude` | `number` (-85 to 85) | Center latitude when `map_position: custom`. |
| `map_longitude` | `number` (-180 to 180) | Center longitude when `map_position: custom`. |
| `map_zoom` | `integer` (0 to 22) | Zoom magnification level (0 = whole world, 18+ = street/building level). |
| `map_pannable` | `boolean` (`true`/`false`) | Toggle user drag and panning interaction. Default is `true`. |
| `map_zoomable` | `boolean` (`true`/`false`) | Toggle user scroll/pinch zoom interaction. Default is `true`. |

### 3. Marker & Point Customization
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_marker_type` | `string` (`'circle'`, `'icon'`, `'circle_and_icon'`, `'none'`) | Shape style for points. Default is `'circle'`. |
| `map_marker_icon_name` | `string` (e.g. `'airplane'`, `'building'`, `'car'`, `'coffee'`, `'house'`, `'person'`, `'shopping_cart'`, `'star'`, `'truck'`) | Pre-built icon identifier when `map_marker_type` includes icon. |
| `map_marker_radius_mode` | `string` (`'proportional_value'`, `'equal_to_value'`, `'fixed'`) | Radius calculation mode. Default is `'proportional_value'`. |
| `map_marker_units` | `string` (`'meters'`, `'pixels'`) | Measurement unit for marker radius. Default is `'meters'`. |
| `map_marker_radius_min` | `number` | Minimum radius floor in pixels/meters for value-scaled points (recommended: 3 to 10). |
| `map_marker_radius_max` | `number` | Maximum radius ceiling in pixels/meters for value-scaled points (recommended: 15 to 30). |
| `map_marker_radius_fixed` | `number` | Fixed radius value when `map_marker_radius_mode: fixed`. |
| `map_marker_proportional_scale_type` | `string` (`'linear'`, `'log'`) | Scaling function for point sizes. Use `'log'` for highly skewed volume metrics. |
| `map_marker_color_mode` | `string` (`'value'`, `'fixed'`) | Color markers dynamically along a color scale or by fixed palette. |
| `map_marker_color` | `list of hex strings` (e.g. `["#1A73E8"]`) | Explicit hex color list for fixed markers or pivoted categories. |

### 4. Value Colors & Dual-Axis Mapping
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_value_colors` | `list of hex strings` | Sequential/diverging gradient color palette for value-based shading. |
| `quantize_map_value_colors` | `boolean` (`true`/`false`) | Discretize continuous gradient colors into distinct color steps. |
| `reverse_map_value_colors` | `boolean` (`true`/`false`) | Invert the color gradient direction. |
| `map_value_scale_clamp_min` | `number` | Minimum metric cutoff bound for color scaling. |
| `map_value_scale_clamp_max` | `number` | Maximum metric cutoff bound for color scaling. |
| `map_dual_axis` | `boolean` (`true`/`false`) | Enable dual-metric mapping when plotting two measures simultaneously. |
| `map_dual_axis_opacity` | `number` (0.3 to 0.7) | Opacity of greyscale overlap layer on dual-axis maps. Default is 0.5. |

### 5. Heatmap & 3D Extrusion
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `heatmap_gridlines` | `boolean` (`true`/`false`) | Render gridlines over automagic heatmap tiles. |
| `heatmap_gridlines_empty` | `boolean` (`true`/`false`) | Render gridlines over empty geographic regions. |
| `heatmap_opacity` | `number` (0.0 to 1.0) | Opacity multiplier for heatmap layer. Default is 0.5. |
| `heatmap_intensity` | `number` (0 to 10) | Density intensity multiplier for density heatmaps. |
| `heatmap_threshold` | `number` (0.0 to 1.0) | Cutoff threshold for density heatmap rendering. |
| `elevation_scale` | `number` (1 to 5000) | Height multiplier for 3D extruded heatmap bars. |
| `hexagon_radius` | `number` (500 to 200000) | Hexagon grid cell radius in meters for 3D heatmaps. |

### 6. Built-In Google Maps Layers
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_transit_layer` | `boolean` (`true`/`false`) | Toggle Google Maps real-time public transit line overlay. |
| `map_traffic_layer` | `boolean` (`true`/`false`) | Toggle Google Maps live traffic condition overlay. |
| `map_bicycling_layer` | `boolean` (`true`/`false`) | Toggle Google Maps dedicated bicycling route overlay. |
| `map_street_view` | `boolean` (`true`/`false`) | Enable Google Street View pegman navigation control. |

### 7. Custom TopoJSON Region Layers
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `map_use_custom_layer` | `boolean` (`true`/`false`) | Enable custom TopoJSON polygon boundary overlay. |
| `map_url` | `string` (HTTPS URL) | Public or CDN URL to external TopoJSON file. |
| `map_object_key` | `string` | TopoJSON object key to target. |
| `map_property_key` | `string` | TopoJSON property key matching query region dimension. |
| `map_property_label_key` | `string` | TopoJSON property key containing user-facing region label. |
| `map_render_all_custom_regions` | `boolean` (`true`/`false`) | Render polygon boundaries even for regions with zero data rows. |
| `map_unmatched_region_color` | `string` (hex code) | Color for empty/unmatched custom regions. |
| `map_unmatched_region_opacity` | `number` (0.0 to 1.0) | Opacity for empty/unmatched custom regions. |

### 8. Labels, Legends & Tooltips
| Parameter | Type / Values | Description |
| :--- | :--- | :--- |
| `show_legend` | `boolean` (`true`/`false`) | Toggle legend visibility. Default is `true`. |
| `show_view_names` | `boolean` (`true`/`false`) | Show full view name in tooltip titles. Default is `false`. |
| `show_region_field` | `boolean` (`true`/`false`) | Show region name inside hover tooltip. Default is `true`. |
| `draw_map_labels_above_data` | `boolean` (`true`/`false`) | Sandwich layer: render city and street text above polygons/heatmaps. Available for `'light'`, `'dark'`, and `'satellite_streets'`. |
| `map_always_display_coordinates` | `boolean` (`true`/`false`) | Show raw lat/long coordinates in tooltip even if name dimension is present. |

---

## Production LookML Example: `looker_google_map`

```yaml
- name: store_locations_traffic
  title: "Store Locations & Delivery Volume"
  model: thelook
  explore: orders
  type: looker_google_map
  fields: [distribution_centers.location, distribution_centers.name, orders.count]
  filters:
    distribution_centers.location: "-NULL"
  sorts: [orders.count desc]
  limit: 500
  # Map Position & Styling
  map_tile_provider: light
  map_position: fit_data
  map_pannable: true
  map_zoomable: true
  # Marker Proportions & Bounds
  map_marker_type: circle
  map_marker_radius_mode: proportional_value
  map_marker_radius_min: 3
  map_marker_radius_max: 18
  map_marker_units: pixels
  map_marker_color_mode: value
  map_value_colors: ["#E8F0FE", "#4285F4", "#1967D2", "#0D47A1"]
  # Google Layers & Labels
  map_traffic_layer: true
  draw_map_labels_above_data: true
  show_legend: true
  show_view_names: false
  row: 8
  col: 0
  width: 24
  height: 9
```
