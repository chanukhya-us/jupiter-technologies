# Jupiter Technologies Chart System

## Overview
Complete rewrite of the charting system for clean, reliable data visualization using Chart.js.

## Architecture

### Files
- **`app/static/js/charts.js`** - Main chart initialization and rendering logic
- **`app/static/vendor/chart.umd.min.js`** - Chart.js library (v4.x)
- **`app/static/css/app.css`** - Chart container styling
- **`app/templates/partials/charts.html`** - Donut chart macro
- **`app/templates/base.html`** - Script loading

## Chart Types

### 1. Donut Charts
Used for status distributions, category breakdowns, and proportional data.

**HTML Structure:**
```html
<canvas 
  class="rt-donut-chart"
  data-labels='["Active", "Pending", "Completed"]'
  data-values='[25, 15, 40]'
  data-total="80"
></canvas>
```

**Features:**
- Center text showing total
- Color-coded segments
- Hover tooltips with percentages
- Responsive sizing
- Legend with percentages

**Used On:**
- Candidates page (status, source)
- Jobs page (status, owner)
- Submissions page (status, recruiter)
- Employees page (status, type)
- Projects page (status, client)
- Dashboard (all status distributions)

### 2. Line Charts
Used for trends over time, growth patterns, and time-series data.

**HTML Structure:**
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="line"
  data-labels='["Mon", "Tue", "Wed", "Thu", "Fri"]'
  data-datasets='[{
    "label": "Candidates",
    "data": [12, 19, 15, 25, 22],
    "borderColor": "#0f62fe",
    "backgroundColor": "rgba(15, 98, 254, 0.1)",
    "fill": true,
    "tension": 0.4
  }]'
></canvas>
```

**Features:**
- Smooth curves (tension: 0.4)
- Gradient fill under line
- Point markers on hover
- Multiple datasets support
- Responsive grid

**Used On:**
- Candidates page (30-day growth trend)
- Jobs page (30-day opening trend)
- Dashboard (hiring activity, timesheet velocity)
- Marketer reports (activity trends)

### 3. Bar Charts
Used for comparisons, volume data, and categorical metrics.

**HTML Structure:**
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="bar"
  data-labels='["Jan", "Feb", "Mar", "Apr"]'
  data-datasets='[{
    "label": "Jobs",
    "data": [5, 8, 12, 7],
    "backgroundColor": "#24a148",
    "borderRadius": 6
  }]'
></canvas>
```

**Features:**
- Rounded corners (6px)
- Max bar thickness (40px)
- Stacked support
- Horizontal orientation support
- Multiple datasets

**Used On:**
- Dashboard (submission funnel)
- Marketer reports (completion vs missed)

## Data Attributes

### Common Attributes
- `class` - Chart type class (`rt-donut-chart` or `rt-series-chart`)
- `data-labels` - JSON array of labels
- `data-total` - Total count (donut only)

### Series Chart Attributes
- `data-chart-type` - Chart type (`line`, `bar`, `mixed`)
- `data-datasets` - JSON array of dataset objects
- `data-show-legend` - Show/hide legend (`true`/`false`)
- `data-legend-position` - Legend position (`top`, `bottom`, `left`, `right`)
- `data-horizontal` - Horizontal bars (`true`/`false`)
- `data-stacked` - Stacked bars/areas (`true`/`false`)

### Dataset Object Properties
```javascript
{
  "type": "line",              // Chart type for this dataset
  "label": "Series Name",      // Legend label
  "data": [1, 2, 3, 4],       // Data points
  "borderColor": "#0f62fe",    // Line/border color
  "backgroundColor": "rgba()", // Fill/bar color
  "fill": true,                // Fill under line
  "tension": 0.4,              // Line smoothness (0-1)
  "borderRadius": 6,           // Bar corner radius
  "borderWidth": 2             // Line/border width
}
```

## Color Palette

### Primary Colors
- **Blue**: `#0f62fe` - Primary actions, candidates
- **Green**: `#24a148` - Success, jobs, completed
- **Orange**: `#ff832b` - Warnings, follow-ups
- **Red**: `#da1e28` - Errors, rejected, missed
- **Purple**: `#8b5cf6` - Interviews, special
- **Cyan**: `#06b6d4` - Info, secondary
- **Yellow**: `#f1c21b` - Caution, pending
- **Pink**: `#ee5396` - Accent, highlights

### Usage Guidelines
- Use blue for primary metrics and trends
- Use green for positive outcomes
- Use red for negative outcomes
- Use orange for attention items
- Maintain consistent colors across related charts

## CSS Classes

### Container Classes
- `.rt-graph-card` - Main graph container with shadow
- `.rt-graph-card-hero` - Larger hero graph
- `.rt-chart-card` - Donut chart container
- `.rt-chart-grid` - 2-column grid for charts

### Canvas Wrappers
- `.rt-graph-canvas-wrap` - Line/bar chart wrapper (200px height)
- `.rt-graph-canvas-wrap-hero` - Hero chart wrapper (278px height)
- `.rt-graph-canvas-wrap-compact` - Compact wrapper (210px height)
- `.rt-chart-canvas-wrap` - Donut chart wrapper (170px max)

### Content Classes
- `.rt-graph-head` - Chart header with title
- `.rt-graph-title` - Chart title
- `.rt-graph-subtitle` - Chart description
- `.rt-chart-total` - Total count badge
- `.rt-chart-legend` - Legend list
- `.rt-chart-empty` - Empty state message

## JavaScript API

### Initialization
Charts are automatically initialized on page load:
```javascript
// Automatic initialization
document.addEventListener('DOMContentLoaded', function() {
  JupiterCharts.init();
});
```

### Manual Initialization
```javascript
// Initialize all charts
JupiterCharts.init();

// Initialize specific donut chart
JupiterCharts.renderDonut(canvasElement);

// Initialize specific series chart
JupiterCharts.renderSeries(canvasElement);
```

### Console Logging
The chart system logs initialization progress:
```
Initializing Jupiter Charts...
Donut chart rendered: 4 segments
Series chart rendered: line 1 datasets
Charts initialized successfully
```

## Backend Integration

### Python Route Example
```python
from datetime import datetime, timedelta
from collections import defaultdict

@app.route('/candidates')
def list_candidates():
    # Get data
    candidates = Candidate.query.all()
    
    # Build trend data
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=29)
    
    by_date = defaultdict(int)
    for candidate in candidates:
        if candidate.created_at.date() >= thirty_days_ago:
            by_date[candidate.created_at.date()] += 1
    
    # Build labels and data
    trend_labels = []
    trend_data = []
    current_date = thirty_days_ago
    while current_date <= today:
        trend_labels.append(current_date.strftime("%m/%d"))
        trend_data.append(by_date.get(current_date, 0))
        current_date += timedelta(days=1)
    
    trend_graph = {
        "labels": trend_labels,
        "datasets": [{
            "label": "New Candidates",
            "data": trend_data,
            "borderColor": "#0f62fe",
            "backgroundColor": "rgba(15, 98, 254, 0.1)",
            "fill": True,
            "tension": 0.4,
        }],
        "is_empty": sum(trend_data) == 0,
        "total": sum(trend_data),
    }
    
    return render_template('candidates/list.html', 
                         trend_graph=trend_graph)
```

### Template Example
```html
<section class="rt-graph-card">
  <div class="rt-graph-head">
    <div>
      <h2 class="rt-graph-title">Candidate Growth Trend</h2>
      <p class="rt-graph-subtitle">New candidates over 30 days</p>
    </div>
    <span class="rt-chart-total">{{ trend_graph.total }} new</span>
  </div>
  
  {% if trend_graph.is_empty %}
  <p class="rt-chart-empty">No data available</p>
  {% else %}
  <div class="rt-graph-canvas-wrap">
    <canvas
      class="rt-series-chart"
      data-chart-type="line"
      data-labels="{{ trend_graph.labels | tojson }}"
      data-datasets="{{ trend_graph.datasets | tojson }}"
      data-show-legend="false"
    ></canvas>
  </div>
  {% endif %}
</section>
```

## Responsive Behavior

### Desktop (>992px)
- Full chart heights
- 2-column chart grids
- All animations enabled

### Tablet (640px-992px)
- Adjusted chart heights
- Single column grids
- Simplified animations

### Mobile (<640px)
- Compact chart heights (190px)
- Single column layout
- Touch-optimized interactions

## Performance

### Optimizations
- Lazy canvas initialization
- Hardware-accelerated animations
- Efficient data parsing
- Minimal DOM manipulation
- Cached color calculations

### Load Times
- Chart.js: ~200KB (minified)
- charts.js: ~5KB
- Total overhead: ~205KB
- Initialization: <100ms

## Troubleshooting

### Charts Not Appearing
1. Check browser console for errors
2. Verify Chart.js is loaded: `typeof Chart !== 'undefined'`
3. Verify data attributes are valid JSON
4. Check canvas has proper class (`rt-donut-chart` or `rt-series-chart`)
5. Ensure container has height set

### Data Not Updating
1. Verify JSON encoding in template: `{{ data | tojson }}`
2. Check for JavaScript syntax errors in data
3. Verify data structure matches expected format
4. Check console for parsing errors

### Styling Issues
1. Verify CSS is loaded
2. Check for conflicting styles
3. Ensure canvas wrapper has dimensions
4. Verify responsive breakpoints

## Browser Support

### Supported Browsers
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Required Features
- Canvas API
- ES6 JavaScript
- CSS Grid & Flexbox
- JSON parsing

## Testing

### Manual Testing
1. Open test_charts.html in browser
2. Verify all three chart types render
3. Check hover interactions
4. Test responsive behavior
5. Verify console logs

### Automated Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Tests verify:
# - Chart runtime loads
# - Canvas elements render
# - Data attributes present
# - No JavaScript errors
```

## Future Enhancements

### Planned Features
- [ ] Real-time chart updates
- [ ] Chart export to PNG/SVG
- [ ] Interactive drill-down
- [ ] Custom tooltips
- [ ] Animation preferences
- [ ] Dark mode support
- [ ] More chart types (radar, scatter, bubble)

### Performance Improvements
- [ ] Virtual scrolling for large datasets
- [ ] Web Workers for data processing
- [ ] Progressive chart rendering
- [ ] Lazy loading for off-screen charts

## Summary

The Jupiter Technologies chart system provides:
- ✅ Clean, modern visualizations
- ✅ Simple data attribute API
- ✅ Responsive design
- ✅ Consistent styling
- ✅ Reliable rendering
- ✅ Easy backend integration
- ✅ Comprehensive documentation

**Status**: ✅ Production Ready
**Version**: 2.0 (Complete Rewrite)
**Last Updated**: April 12, 2026
