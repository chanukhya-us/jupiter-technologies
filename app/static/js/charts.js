/**
 * Jupiter Technologies Chart System
 * Clean, simple chart rendering with Chart.js
 */

(function() {
  'use strict';

  // Color palette
  const COLORS = {
    blue: '#0f62fe',
    green: '#24a148',
    orange: '#ff832b',
    red: '#da1e28',
    purple: '#8b5cf6',
    cyan: '#06b6d4',
    yellow: '#f1c21b',
    pink: '#ee5396',
  };

  const CHART_COLORS = [
    COLORS.blue,
    COLORS.green,
    COLORS.orange,
    COLORS.red,
    COLORS.purple,
    COLORS.cyan,
    COLORS.yellow,
    COLORS.pink,
  ];

  /**
   * Safely parse JSON with validation
   */
  function safeJSONParse(str, defaultValue = null) {
    if (!str || typeof str !== 'string') {
      return defaultValue;
    }
    
    // Trim whitespace
    str = str.trim();
    
    // Check for empty or invalid strings
    if (str === '' || str === 'undefined' || str === 'null' || str.length === 0) {
      return defaultValue;
    }
    
    try {
      return JSON.parse(str);
    } catch (e) {
      console.error('JSON parse error:', e.message, 'Input:', str);
      return defaultValue;
    }
  }

  /**
   * Initialize all charts on the page
   */
  function initCharts() {
    console.log('=== Initializing Jupiter Charts ===');
    
    if (typeof Chart === 'undefined') {
      console.error('Chart.js not loaded!');
      return;
    }

    // Set global defaults
    Chart.defaults.font.family = 'system-ui, -apple-system, sans-serif';
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#64748b';

    // Initialize donut charts
    const donutCharts = document.querySelectorAll('canvas.rt-donut-chart');
    console.log(`Found ${donutCharts.length} donut chart(s)`);
    
    donutCharts.forEach((canvas, index) => {
      console.log(`\n--- Processing donut chart ${index + 1}/${donutCharts.length} ---`);
      console.log('Canvas ID:', canvas.id || '(no id)');
      
      try {
        renderDonutChart(canvas);
      } catch (error) {
        console.error(`!!! Error rendering donut chart ${index + 1}:`, error.message);
        console.error('Canvas ID:', canvas.id);
        console.error('Data attributes:', {
          labels: canvas.dataset.labels,
          values: canvas.dataset.values,
          total: canvas.dataset.total
        });
      }
    });

    // Initialize line/bar charts
    const seriesCharts = document.querySelectorAll('canvas.rt-series-chart');
    console.log(`\nFound ${seriesCharts.length} series chart(s)`);
    
    seriesCharts.forEach((canvas, index) => {
      console.log(`\n--- Processing series chart ${index + 1}/${seriesCharts.length} ---`);
      console.log('Canvas ID:', canvas.id || '(no id)');
      
      try {
        renderSeriesChart(canvas);
      } catch (error) {
        console.error(`!!! Error rendering series chart ${index + 1}:`, error.message);
        console.error('Canvas ID:', canvas.id);
        console.error('Data attributes:', {
          labels: canvas.dataset.labels,
          datasets: canvas.dataset.datasets
        });
      }
    });

    console.log('\n=== Charts initialization complete ===');
  }

  /**
   * Render a donut chart
   */
  function renderDonutChart(canvas) {
    const labelsAttr = canvas.dataset.labels;
    const valuesAttr = canvas.dataset.values;
    const totalAttr = canvas.dataset.total;
    
    console.log('  → Validating attributes...');
    console.log('    labels attr:', typeof labelsAttr, labelsAttr ? `"${labelsAttr.substring(0, 50)}..."` : 'undefined/null');
    console.log('    values attr:', typeof valuesAttr, valuesAttr ? `"${valuesAttr.substring(0, 50)}..."` : 'undefined/null');
    console.log('    total attr:', typeof totalAttr, totalAttr);
    
    // Parse with safe parser
    const labels = safeJSONParse(labelsAttr, []);
    const values = safeJSONParse(valuesAttr, []);
    const total = totalAttr ? parseInt(totalAttr) : 0;
    
    console.log('  → Parsed data:');
    console.log('    labels:', labels);
    console.log('    values:', values);
    console.log('    total:', total);

    if (!Array.isArray(labels) || !Array.isArray(values) || labels.length === 0 || values.length === 0 || total === 0) {
      console.log('  ✗ Skipping: invalid or empty data');
      return;
    }
    
    console.log('  → Creating chart with', labels.length, 'segments...');

    const colors = labels.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]);

    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: '#ffffff',
          borderWidth: 2,
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#1e293b',
            padding: 12,
            cornerRadius: 8,
            titleFont: {
              size: 13,
              weight: '600'
            },
            bodyFont: {
              size: 12
            },
            callbacks: {
              label: function(context) {
                const value = context.parsed;
                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0';
                return `${context.label}: ${value} (${percentage}%)`;
              }
            }
          }
        }
      },
      plugins: [{
        id: 'centerText',
        afterDraw: function(chart) {
          const ctx = chart.ctx;
          const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
          const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;

          ctx.save();
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          
          // Draw total
          ctx.fillStyle = '#1e293b';
          ctx.font = 'bold 20px system-ui';
          ctx.fillText(total.toString(), centerX, centerY - 8);
          
          // Draw label
          ctx.fillStyle = '#64748b';
          ctx.font = '12px system-ui';
          ctx.fillText('Total', centerX, centerY + 12);
          
          ctx.restore();
        }
      }]
    });

    console.log('  ✓ Donut chart rendered successfully');
  }

  /**
   * Render a line or bar chart
   */
  function renderSeriesChart(canvas) {
    const labelsAttr = canvas.dataset.labels;
    const datasetsAttr = canvas.dataset.datasets;
    
    console.log('  → Validating attributes...');
    console.log('    labels attr:', typeof labelsAttr, labelsAttr ? `"${labelsAttr.substring(0, 50)}..."` : 'undefined/null');
    console.log('    datasets attr:', typeof datasetsAttr, datasetsAttr ? `"${datasetsAttr.substring(0, 50)}..."` : 'undefined/null');
    
    // Parse with safe parser
    const labels = safeJSONParse(labelsAttr, []);
    const datasets = safeJSONParse(datasetsAttr, []);
    
    console.log('  → Parsed data:');
    console.log('    labels:', labels);
    console.log('    datasets:', datasets);
    
    const chartType = canvas.dataset.chartType || 'line';
    const showLegend = canvas.dataset.showLegend !== 'false';
    const horizontal = canvas.dataset.horizontal === 'true';
    const stacked = canvas.dataset.stacked === 'true';

    if (!Array.isArray(labels) || !Array.isArray(datasets) || labels.length === 0 || datasets.length === 0) {
      console.log('  ✗ Skipping: invalid or empty data');
      return;
    }
    
    console.log('  → Creating', chartType, 'chart with', datasets.length, 'dataset(s)...');

    // Process datasets
    const processedDatasets = datasets.map((dataset, index) => {
      const type = dataset.type || chartType;
      const color = dataset.borderColor || dataset.backgroundColor || CHART_COLORS[index % CHART_COLORS.length];
      
      const processed = {
        type: type,
        label: dataset.label || `Series ${index + 1}`,
        data: dataset.data || [],
        borderColor: color,
        backgroundColor: type === 'line' 
          ? (dataset.backgroundColor || color.replace(')', ', 0.1)').replace('rgb', 'rgba'))
          : (dataset.backgroundColor || color),
        borderWidth: type === 'line' ? 2 : 1,
        tension: type === 'line' ? (dataset.tension || 0.4) : 0,
        fill: type === 'line' ? (dataset.fill !== undefined ? dataset.fill : true) : false,
        pointRadius: type === 'line' ? 3 : 0,
        pointHoverRadius: type === 'line' ? 5 : 0,
        borderRadius: type === 'bar' ? (dataset.borderRadius || 6) : 0,
        maxBarThickness: type === 'bar' ? 40 : undefined,
      };

      return processed;
    });

    new Chart(canvas, {
      type: chartType,
      data: {
        labels: labels,
        datasets: processedDatasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: horizontal ? 'y' : 'x',
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            display: showLegend,
            position: canvas.dataset.legendPosition || 'top',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 12,
                weight: '500'
              }
            }
          },
          tooltip: {
            backgroundColor: '#1e293b',
            padding: 12,
            cornerRadius: 8,
            titleFont: {
              size: 13,
              weight: '600'
            },
            bodyFont: {
              size: 12
            }
          }
        },
        scales: {
          x: {
            stacked: stacked,
            grid: {
              display: !horizontal,
              color: 'rgba(148, 163, 184, 0.15)',
              drawBorder: false,
            },
            border: {
              display: false
            },
            ticks: {
              color: '#64748b',
              font: {
                size: 11
              },
              maxRotation: 0,
              autoSkipPadding: 10,
            }
          },
          y: {
            stacked: stacked,
            beginAtZero: true,
            grid: {
              color: 'rgba(148, 163, 184, 0.15)',
              drawBorder: false,
            },
            border: {
              display: false
            },
            ticks: {
              color: '#64748b',
              font: {
                size: 11
              },
              precision: 0,
            }
          }
        }
      }
    });

    console.log('  ✓ Series chart rendered successfully');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCharts);
  } else {
    initCharts();
  }

  // Export for manual initialization
  window.JupiterCharts = {
    init: initCharts,
    renderDonut: renderDonutChart,
    renderSeries: renderSeriesChart
  };

})();
