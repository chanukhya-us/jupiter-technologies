# Quick Start Guide - Jupiter Charts

## Verify Charts Are Working

### 1. Open the Application
```bash
# Start the application
source .venv/bin/activate
flask --app app.py run --port 5001 --debug

# Open in browser
http://127.0.0.1:5001
```

### 2. Check the Dashboard
- Login with: `admin` / `admin123`
- Navigate to Dashboard
- You should see:
  - ✅ Hiring Activity Trend (line graph)
  - ✅ Timesheet Velocity (bar graph)
  - ✅ Submission Funnel (horizontal bars)
  - ✅ 5 donut charts (status distributions)

### 3. Check Candidates Page
- Navigate to Candidates
- You should see:
  - ✅ 30-Day Growth Trend (blue line graph)
  - ✅ Status donut chart
  - ✅ Source donut chart

### 4. Check Jobs Page
- Navigate to Jobs
- You should see:
  - ✅ 30-Day Opening Trend (green line graph)
  - ✅ Status donut chart
  - ✅ Owner donut chart

### 5. Check Submissions Page
- Navigate to Submissions
- You should see:
  - ✅ 4 KPI metric cards
  - ✅ Status donut chart
  - ✅ Recruiter donut chart

### 6. Check Browser Console
Press F12 (or Cmd+Option+I on Mac) and look for:
```
Initializing Jupiter Charts...
Donut chart rendered: X segments
Series chart rendered: line 1 datasets
Charts initialized successfully
```

## Troubleshooting

### Charts Not Appearing?

**Step 1: Check Console**
```javascript
// Open browser console (F12)
// Type:
typeof Chart
// Should return: "function"

typeof JupiterCharts
// Should return: "object"
```

**Step 2: Check Network Tab**
- Open Network tab in browser dev tools
- Refresh page
- Look for:
  - ✅ `chart.umd.min.js` - Status 200 or 304
  - ✅ `charts.js` - Status 200 or 304

**Step 3: Check HTML**
- Right-click on chart area
- Select "Inspect Element"
- Look for:
```html
<canvas class="rt-donut-chart" data-labels="[...]" ...></canvas>
<!-- or -->
<canvas class="rt-series-chart" data-labels="[...]" ...></canvas>
```

**Step 4: Hard Refresh**
- Windows/Linux: Ctrl + F5
- Mac: Cmd + Shift + R

### Still Not Working?

**Check Test Page:**
```bash
# Open test_charts.html in browser
open test_charts.html
# or
firefox test_charts.html
```

If test page works but app doesn't:
- Check template syntax
- Verify data is being passed from backend
- Check for JavaScript errors in console

If test page doesn't work:
- Verify Chart.js is loaded
- Check charts.js for syntax errors
- Verify browser supports Canvas API

## Adding a New Chart

### Backend (Python)
```python
# In your route file (e.g., app/candidates/routes.py)
from datetime import datetime, timedelta
from collections import defaultdict

@app.route('/my-page')
def my_page():
    # Calculate trend data
    today = datetime.now().date()
    days_ago = today - timedelta(days=29)
    
    by_date = defaultdict(int)
    for item in my_items:
        if item.created_at.date() >= days_ago:
            by_date[item.created_at.date()] += 1
    
    # Build chart data
    labels = []
    data = []
    current = days_ago
    while current <= today:
        labels.append(current.strftime("%m/%d"))
        data.append(by_date.get(current, 0))
        current += timedelta(days=1)
    
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "My Metric",
            "data": data,
            "borderColor": "#0f62fe",
            "backgroundColor": "rgba(15, 98, 254, 0.1)",
            "fill": True,
            "tension": 0.4
        }],
        "is_empty": sum(data) == 0,
        "total": sum(data)
    }
    
    return render_template('my-page.html', chart_data=chart_data)
```

### Frontend (HTML)
```html
<!-- In your template (e.g., templates/my-page.html) -->
<section class="rt-graph-card">
  <div class="rt-graph-head">
    <div>
      <h2 class="rt-graph-title">My Trend</h2>
      <p class="rt-graph-subtitle">Description of the trend</p>
    </div>
    <span class="rt-chart-total">{{ chart_data.total }} total</span>
  </div>
  
  {% if chart_data.is_empty %}
  <p class="rt-chart-empty">No data available</p>
  {% else %}
  <div class="rt-graph-canvas-wrap">
    <canvas
      class="rt-series-chart"
      data-chart-type="line"
      data-labels="{{ chart_data.labels | tojson }}"
      data-datasets="{{ chart_data.datasets | tojson }}"
      data-show-legend="false"
    ></canvas>
  </div>
  {% endif %}
</section>
```

### That's It!
The chart will automatically initialize when the page loads.

## Chart Types Quick Reference

### Line Chart (Trends)
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="line"
  data-labels='["Mon", "Tue", "Wed"]'
  data-datasets='[{
    "label": "Sales",
    "data": [10, 20, 15],
    "borderColor": "#0f62fe",
    "backgroundColor": "rgba(15, 98, 254, 0.1)",
    "fill": true,
    "tension": 0.4
  }]'
></canvas>
```

### Bar Chart (Comparisons)
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="bar"
  data-labels='["Q1", "Q2", "Q3"]'
  data-datasets='[{
    "label": "Revenue",
    "data": [100, 150, 120],
    "backgroundColor": "#24a148",
    "borderRadius": 6
  }]'
></canvas>
```

### Donut Chart (Distributions)
```html
<canvas 
  class="rt-donut-chart"
  data-labels='["Active", "Pending", "Done"]'
  data-values='[25, 15, 40]'
  data-total="80"
></canvas>
```

## Color Reference

```javascript
Blue:   #0f62fe  // Primary, candidates
Green:  #24a148  // Success, jobs
Orange: #ff832b  // Warnings
Red:    #da1e28  // Errors, rejected
Purple: #8b5cf6  // Special
Cyan:   #06b6d4  // Info
Yellow: #f1c21b  // Caution
Pink:   #ee5396  // Accent
```

## Common Patterns

### Multiple Datasets
```javascript
data-datasets='[
  {
    "label": "Series 1",
    "data": [10, 20, 15],
    "borderColor": "#0f62fe"
  },
  {
    "label": "Series 2",
    "data": [5, 15, 25],
    "borderColor": "#24a148"
  }
]'
```

### Stacked Bars
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="bar"
  data-stacked="true"
  ...
></canvas>
```

### Horizontal Bars
```html
<canvas 
  class="rt-series-chart"
  data-chart-type="bar"
  data-horizontal="true"
  ...
></canvas>
```

## Need More Help?

- **Full Documentation**: See `CHARTS_SYSTEM.md`
- **UI Details**: See `UI_ENHANCEMENTS.md`
- **Project Summary**: See `FINAL_SUMMARY.md`
- **Test Page**: Open `test_charts.html`

## Quick Commands

```bash
# Run tests
python -m pytest tests/ -v

# Start app
flask --app app.py run --port 5001 --debug

# Check if Chart.js exists
ls -lh app/static/vendor/chart.umd.min.js

# Check if charts.js exists
ls -lh app/static/js/charts.js
```

## Success Checklist

- [ ] Application starts without errors
- [ ] Dashboard shows all charts
- [ ] Candidates page shows trend graph
- [ ] Jobs page shows trend graph
- [ ] Submissions page shows KPI cards
- [ ] Console shows "Charts initialized successfully"
- [ ] No JavaScript errors in console
- [ ] Charts respond to hover
- [ ] All 20 tests pass

If all checked, you're good to go! 🎉

---

**Quick Start Version**: 1.0
**Last Updated**: April 12, 2026
