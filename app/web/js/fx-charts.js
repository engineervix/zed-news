/**
 * FX Charts - Foreign Exchange Rate Visualization
 * Uses Alpine.js for reactivity and Chart.js for charts
 */

import Chart from "chart.js/auto";
import "chartjs-adapter-date-fns";

// Register FX components using the global registration system
function registerFXComponents(Alpine) {
  console.log("Registering FX components with Alpine");

  // FX Data Store
  Alpine.store("fxData", {
    loading: true,
    error: null,
    currentRates: {},
    historicalData: [],
    trends: {},
    metadata: {},
    fx_current: {},

    async loadData() {
      this.loading = true;
      this.error = null;

      try {
        // Load historical data
        const historicalResponse = await fetch("/js/fx_data.json");
        if (!historicalResponse.ok) {
          throw new Error(`HTTP error! status: ${historicalResponse.status}`);
        }
        const historicalData = await historicalResponse.json();

        // Load current data with dates
        const currentResponse = await fetch("/js/fx_current.json");
        if (!currentResponse.ok) {
          throw new Error(`HTTP error! status: ${currentResponse.status}`);
        }
        const currentData = await currentResponse.json();

        this.currentRates =
          (currentData.current_rates && currentData.current_rates.rates) || {};
        this.historicalData = historicalData.historical_data || [];
        this.trends = currentData.trends || {};
        this.metadata = historicalData.metadata || {};
        this.fx_current = currentData;

        console.log("FX data loaded successfully");
      } catch (error) {
        console.error("Failed to load FX data:", error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },
  });

  // FX Widget Component
  Alpine.data("fxWidget", () => ({
    init() {
      // Load data when the component initializes
      this.$store.fxData.loadData();
    },

    get loading() {
      return this.$store.fxData.loading;
    },
    get error() {
      return this.$store.fxData.error;
    },
    get currentRates() {
      return this.$store.fxData.currentRates;
    },
    get trends() {
      return this.$store.fxData.trends;
    },
    get fx_current() {
      return this.$store.fxData.fx_current;
    },

    formatRate(value) {
      if (!value) return "N/A";
      return new Intl.NumberFormat("en-ZM", {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      }).format(value);
    },

    getTrendClass(direction) {
      const classes = {
        up: "text-success",
        down: "text-danger",
        stable: "text-muted",
      };
      return classes[direction] || classes.stable;
    },

    getTrendIcon(direction) {
      const icons = {
        up: "fas fa-arrow-up",
        down: "fas fa-arrow-down",
        stable: "fas fa-minus",
      };
      return icons[direction] || icons.stable;
    },
  }));

  // FX Charts Component
  Alpine.data("fxCharts", () => ({
    selectedCurrency: "USD",
    selectedPeriod: "1Y",
    showNormalizedData: true,
    chart: null,

    currencies: [
      { code: "USD", name: "US Dollar", symbol: "$" },
      { code: "GBP", name: "British Pound", symbol: "£" },
      { code: "EUR", name: "Euro", symbol: "€" },
      { code: "ZAR", name: "South African Rand", symbol: "R" },
    ],

    periods: [
      { code: "1Y", name: "1 Year" },
      { code: "2Y", name: "2 Years" },
      { code: "5Y", name: "5 Years" },
      { code: "ALL", name: "All Time" },
    ],

    init() {
      // Load data when component initializes
      this.$store.fxData.loadData();

      // Watch for data changes
      this.$watch("$store.fxData.loading", (loading) => {
        if (!loading && !this.$store.fxData.error) {
          this.$nextTick(() => {
            this.renderChart();
          });
        }
      });

      // Watch for filter changes
      this.$watch("selectedCurrency", () => this.renderChart());
      this.$watch("selectedPeriod", () => this.renderChart());
      this.$watch("showNormalizedData", () => this.renderChart());

      // Watch for theme changes
      this.themeObserver = new MutationObserver(() => {
        if (this.chart) {
          this.renderChart();
        }
      });

      // Handle window resize for responsive chart updates
      let resizeTimeout;
      this.resizeHandler = () => {
        if (this.chart) {
          // Clear any existing timeout
          clearTimeout(resizeTimeout);

          // Debounce the resize handling
          resizeTimeout = setTimeout(() => {
            // Use requestAnimationFrame to ensure DOM is ready after resize
            requestAnimationFrame(() => {
              // Check if canvas is still visible and has dimensions
              const canvas = this.$refs.chartCanvas;
              if (canvas && canvas.offsetWidth > 0 && canvas.offsetHeight > 0) {
                this.chart.resize();
                // Update chart options for new screen size
                this.updateChartForScreenSize();
              } else {
                // If canvas is not properly sized, re-render completely
                setTimeout(() => {
                  this.renderChart();
                }, 100);
              }
            });
          }, 150); // 150ms debounce delay
        }
      };

      // Handle orientation change specifically for mobile devices
      this.orientationHandler = () => {
        // Delay to allow the orientation change to complete
        setTimeout(() => {
          if (this.chart) {
            this.renderChart();
          }
        }, 300);
      };

      window.addEventListener("resize", this.resizeHandler);
      window.addEventListener("orientationchange", this.orientationHandler);

      // Add intersection observer to handle when the chart becomes visible
      this.intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          const chartCanvas = this.$refs.chartCanvas;
          if (
            entry.isIntersecting &&
            chartCanvas &&
            entry.target === chartCanvas.parentElement
          ) {
            // Chart container is now visible, ensure chart is rendered
            if (
              !this.chart &&
              !this.$store.fxData.loading &&
              !this.$store.fxData.error
            ) {
              this.$nextTick(() => {
                this.renderChart();
              });
            }
          }
        });
      });

      // Start observing the chart container when it's available
      this.$nextTick(() => {
        const chartCanvas = this.$refs.chartCanvas;
        const chartContainer = chartCanvas && chartCanvas.parentElement;
        if (chartContainer) {
          this.intersectionObserver.observe(chartContainer);
        }
      });

      // Observe theme changes on document root and body
      this.themeObserver.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-bs-theme"],
      });
      this.themeObserver.observe(document.body, {
        attributes: true,
        attributeFilter: ["data-bs-theme"],
      });
    },

    destroy() {
      // Clean up observer when component is destroyed
      if (this.themeObserver) {
        this.themeObserver.disconnect();
      }

      // Clean up intersection observer
      if (this.intersectionObserver) {
        this.intersectionObserver.disconnect();
      }

      // Clean up resize listener
      if (this.resizeHandler) {
        window.removeEventListener("resize", this.resizeHandler);
      }

      // Clean up orientation change listener
      if (this.orientationHandler) {
        window.removeEventListener(
          "orientationchange",
          this.orientationHandler
        );
      }

      if (this.chart) {
        this.chart.destroy();
      }
    },

    updateChartForScreenSize() {
      if (!this.chart) return;

      const isMobile = window.innerWidth < 768;

      // Update x-axis tick configuration based on screen size
      this.chart.options.scales.x.ticks.maxTicksLimit = isMobile ? 6 : 12;
      this.chart.options.scales.x.ticks.maxRotation = isMobile ? 45 : 30;

      // Update point radius for mobile
      this.chart.data.datasets[0].pointRadius = isMobile ? 1 : 2;
      this.chart.data.datasets[0].pointHoverRadius = isMobile ? 4 : 5;

      // Update the chart
      this.chart.update("none"); // Use 'none' animation mode for immediate update
    },

    getFilteredData() {
      const fxStore = this.$store.fxData;
      let data = [...fxStore.historicalData];

      // Filter by normalized data preference
      if (!this.showNormalizedData) {
        data = data.filter((d) => !d.normalized);
      }

      // Filter by period
      if (this.selectedPeriod !== "ALL") {
        const yearsBack = parseInt(this.selectedPeriod.replace("Y", ""));
        const cutoffDate = new Date();
        cutoffDate.setFullYear(cutoffDate.getFullYear() - yearsBack);

        data = data.filter((d) => new Date(d.date) >= cutoffDate);
      }

      return data;
    },

    renderChart() {
      const fxStore = this.$store.fxData;

      if (fxStore.loading || fxStore.error || !fxStore.historicalData.length) {
        return;
      }

      const canvas = this.$refs.chartCanvas;
      if (!canvas) return;

      // Ensure the canvas container has proper dimensions before creating chart
      if (canvas.offsetWidth === 0 || canvas.offsetHeight === 0) {
        // If canvas is not properly sized, retry after a short delay
        setTimeout(() => {
          this.renderChart();
        }, 100);
        return;
      }

      // Destroy existing chart
      if (this.chart) {
        this.chart.destroy();
      }

      const filteredData = this.getFilteredData();

      // Prepare chart data
      const labels = filteredData.map((d) => d.date);
      const chartData = filteredData.map((d) => d[this.selectedCurrency]);

      // Detect dark mode
      const isDarkMode = this.isDarkMode();
      const textColor = isDarkMode ? "#e9ecef" : "#495057";
      const gridColor = isDarkMode
        ? "rgba(255, 255, 255, 0.1)"
        : "rgba(0, 0, 0, 0.1)";
      const tooltipBgColor = isDarkMode
        ? "rgba(33, 37, 41, 0.95)"
        : "rgba(0, 0, 0, 0.8)";

      // Chart configuration
      const config = {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: `${this.selectedCurrency}/ZMW Exchange Rate`,
              data: chartData,
              borderColor: this.getCurrencyColor(this.selectedCurrency),
              backgroundColor: this.getCurrencyColor(
                this.selectedCurrency,
                0.1
              ),
              borderWidth: 2,
              fill: true,
              tension: 0.1,
              pointRadius: 2,
              pointHoverRadius: 5,
              pointBackgroundColor: this.getCurrencyColor(
                this.selectedCurrency
              ),
              pointBorderColor: isDarkMode ? "#fff" : "#000",
              pointBorderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: "index",
          },
          plugins: {
            title: {
              display: true,
              text: `Zambian Kwacha per ${this.selectedCurrency}`,
              color: textColor,
              font: {
                size: 16,
                weight: "bold",
              },
            },
            legend: {
              display: false,
            },
            tooltip: {
              backgroundColor: tooltipBgColor,
              titleColor: isDarkMode ? "#f8f9fa" : "white",
              bodyColor: isDarkMode ? "#f8f9fa" : "white",
              borderColor: this.getCurrencyColor(this.selectedCurrency),
              borderWidth: 1,
              cornerRadius: 8,
              callbacks: {
                title: (context) => {
                  const dataPoint = filteredData[context[0].dataIndex];
                  const date = new Date(dataPoint.date);
                  return date.toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  });
                },
                label: (context) => {
                  const value = context.parsed.y;
                  const dataPoint = filteredData[context.dataIndex];
                  const normalized = dataPoint.normalized
                    ? " (pre-rebase, normalized)"
                    : "";
                  const dataType =
                    dataPoint.period_type === "daily"
                      ? " (daily)"
                      : dataPoint.period_type === "monthly"
                      ? " (monthly avg)"
                      : "";
                  return `${this.selectedCurrency}: ${value.toFixed(
                    3
                  )} ZMW${normalized}${dataType}`;
                },
              },
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              title: {
                display: true,
                text: "Zambian Kwacha (ZMW)",
                color: textColor,
              },
              ticks: {
                color: textColor,
              },
              grid: {
                color: gridColor,
                borderColor: textColor,
              },
            },
            x: {
              type: "time",
              time: {
                parser: "yyyy-MM-dd",
                tooltipFormat: "MMM dd, yyyy",
                displayFormats: {
                  day: "MMM dd",
                  week: "MMM dd",
                  month: "MMM yyyy",
                  quarter: "MMM yyyy",
                  year: "yyyy",
                },
              },
              title: {
                display: true,
                text: "Date",
                color: textColor,
              },
              ticks: {
                color: textColor,
                maxTicksLimit: window.innerWidth < 768 ? 6 : 12,
                autoSkip: true,
                maxRotation: window.innerWidth < 768 ? 45 : 30,
                minRotation: 0,
              },
              grid: {
                display: false,
              },
              border: {
                color: textColor,
              },
            },
          },
        },
      };

      // Create new chart
      this.chart = new Chart(canvas, config);
    },

    isDarkMode() {
      // Check if Bootstrap dark theme is active
      return (
        document.documentElement.getAttribute("data-bs-theme") === "dark" ||
        document.body.getAttribute("data-bs-theme") === "dark"
      );
    },

    getCurrencyColor(currency, alpha = 1) {
      const colors = {
        USD: `rgba(34, 139, 34, ${alpha})`, // Green
        GBP: `rgba(65, 105, 225, ${alpha})`, // Royal Blue
        EUR: `rgba(255, 140, 0, ${alpha})`, // Dark Orange
        ZAR: `rgba(220, 20, 60, ${alpha})`, // Crimson
      };
      return colors[currency] || `rgba(128, 128, 128, ${alpha})`;
    },

    getCurrencyInfo(currency) {
      return this.currencies.find((c) => c.code === currency) || {};
    },

    formatCurrency(value, currency = "ZMW") {
      return new Intl.NumberFormat("en-ZM", {
        style: "currency",
        currency: currency,
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      }).format(value);
    },

    getTrendIcon(direction) {
      const icons = {
        up: "fas fa-arrow-up text-success",
        down: "fas fa-arrow-down text-danger",
        stable: "fas fa-minus text-muted",
      };
      return icons[direction] || icons.stable;
    },
  }));
}

// Register FX components using the global registration system
if (typeof window !== "undefined" && window.registerAlpineComponent) {
  window.registerAlpineComponent(registerFXComponents);
} else {
  // Fallback: wait for the global registration function to be available
  const checkRegistration = () => {
    if (typeof window !== "undefined" && window.registerAlpineComponent) {
      window.registerAlpineComponent(registerFXComponents);
    } else {
      setTimeout(checkRegistration, 50);
    }
  };
  checkRegistration();
}
