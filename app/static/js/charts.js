(function () {
  const DEFAULT_COLORS = [
    "#2563eb",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#06b6d4",
    "#f97316",
    "#84cc16",
  ];

  function parseJSON(rawValue, fallback) {
    if (!rawValue) {
      return fallback;
    }
    try {
      return JSON.parse(rawValue);
    } catch (error) {
      return fallback;
    }
  }

  function centerTextPlugin() {
    return {
      id: "rtCenterText",
      afterDraw(chart) {
        const pluginOptions = chart.config.options.plugins.rtCenterText || {};
        const total = pluginOptions.total;
        if (total === undefined || total === null) {
          return;
        }

        const { ctx, chartArea } = chart;
        if (!chartArea) {
          return;
        }

        const x = (chartArea.left + chartArea.right) / 2;
        const y = (chartArea.top + chartArea.bottom) / 2;
        const label = pluginOptions.label || "Total";

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = "#1e293b";
        ctx.font = "600 18px Arial, sans-serif";
        ctx.fillText(String(total), x, y - 6);
        ctx.fillStyle = "#64748b";
        ctx.font = "12px Arial, sans-serif";
        ctx.fillText(label, x, y + 12);
        ctx.restore();
      },
    };
  }

  function renderCircularChart(canvas) {
    if (!window.Chart || !canvas) {
      return;
    }

    const labels = parseJSON(canvas.dataset.labels, []);
    const values = parseJSON(canvas.dataset.values, []);
    const colors = parseJSON(canvas.dataset.colors, DEFAULT_COLORS);
    const fallbackTotal = values.reduce((sum, value) => sum + Number(value || 0), 0);
    const total = Number(canvas.dataset.total || fallbackTotal);

    if (!labels.length || !values.length || total <= 0) {
      return;
    }

    const chartColors = labels.map((_, index) => colors[index % colors.length]);
    const context = canvas.getContext("2d");

    new window.Chart(context, {
      type: "doughnut",
      data: {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: chartColors,
            borderColor: "#ffffff",
            borderWidth: 2,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "72%",
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(context) {
                const value = Number(context.raw || 0);
                const pct = total ? ((value / total) * 100).toFixed(1) : "0.0";
                return `${context.label}: ${value} (${pct}%)`;
              },
            },
          },
          rtCenterText: {
            total,
            label: canvas.dataset.centerLabel || "Total",
          },
        },
      },
      plugins: [centerTextPlugin()],
    });
  }

  function renderAll() {
    const charts = document.querySelectorAll("canvas.rt-donut-chart");
    charts.forEach((canvas) => renderCircularChart(canvas));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderAll);
  } else {
    renderAll();
  }

  window.JupiterCharts = { renderAll, renderCircularChart };
})();
