/**
 * GridWorks Chart Renderer
 * 
 * High-performance chart rendering engine using HTML5 Canvas.
 * Handles candlestick charts, indicators, volume, and overlays.
 */

class ChartRenderer {
  constructor({ canvas, overlayCanvas, width, height, theme = 'dark' }) {
    this.canvas = canvas;
    this.overlayCanvas = overlayCanvas;
    this.ctx = canvas.getContext('2d');
    this.overlayCtx = overlayCanvas.getContext('2d');
    this.width = width;
    this.height = height;
    this.theme = theme;
    
    // Chart data
    this.data = [];
    this.indicators = {};
    this.drawings = [];
    
    // View state
    this.zoom = { x: 0, y: 0, scale: 1 };
    this.pan = { x: 0, y: 0 };
    
    // Chart configuration
    this.config = {
      padding: { top: 20, right: 60, bottom: 60, left: 20 },
      candleWidth: 8,
      candleSpacing: 2,
      volumeHeight: 0.2, // 20% of chart height
      gridLines: true,
      showVolume: true
    };
    
    // Color schemes
    this.colors = {
      dark: {
        background: '#1a1a1a',
        grid: '#333',
        text: '#ccc',
        upCandle: '#26a69a',
        downCandle: '#ef5350',
        upWick: '#26a69a',
        downWick: '#ef5350',
        volume: '#555',
        crosshair: '#666'
      },
      light: {
        background: '#ffffff',
        grid: '#e1e1e1',
        text: '#333',
        upCandle: '#4caf50',
        downCandle: '#f44336',
        upWick: '#4caf50',
        downWick: '#f44336',
        volume: '#ddd',
        crosshair: '#999'
      }
    };
    
    // Initialize
    this.setCanvasSize(width, height);
  }
  
  setCanvasSize(width, height) {
    this.width = width;
    this.height = height;
    
    // Set actual canvas size
    this.canvas.width = width;
    this.canvas.height = height;
    this.overlayCanvas.width = width;
    this.overlayCanvas.height = height;
    
    // Set display size
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.overlayCanvas.style.width = `${width}px`;
    this.overlayCanvas.style.height = `${height}px`;
    
    // Configure context for high DPI
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.overlayCanvas.width = width * dpr;
    this.overlayCanvas.height = height * dpr;
    
    this.ctx.scale(dpr, dpr);
    this.overlayCtx.scale(dpr, dpr);
  }
  
  setData(data) {
    this.data = data;
    this.calculatePriceRange();
    this.calculateVolumeRange();
  }
  
  setIndicators(indicators) {
    this.indicators = indicators;
  }
  
  setDrawings(drawings) {
    this.drawings = drawings;
  }
  
  setTheme(theme) {
    this.theme = theme;
  }
  
  setZoom(zoom) {
    this.zoom = zoom;
  }
  
  setPan(pan) {
    this.pan = pan;
  }
  
  calculatePriceRange() {
    if (!this.data.length) return;
    
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    
    for (const candle of this.data) {
      minPrice = Math.min(minPrice, candle.low);
      maxPrice = Math.max(maxPrice, candle.high);
    }
    
    // Add 5% padding
    const padding = (maxPrice - minPrice) * 0.05;
    this.priceRange = {
      min: minPrice - padding,
      max: maxPrice + padding
    };
  }
  
  calculateVolumeRange() {
    if (!this.data.length) return;
    
    let maxVolume = 0;
    for (const candle of this.data) {
      maxVolume = Math.max(maxVolume, candle.volume || 0);
    }
    
    this.volumeRange = {
      min: 0,
      max: maxVolume
    };
  }
  
  render() {
    this.clear();
    
    if (!this.data.length) {
      this.renderEmptyState();
      return;
    }
    
    // Draw background
    this.drawBackground();
    
    // Draw grid
    if (this.config.gridLines) {
      this.drawGrid();
    }
    
    // Draw volume (background)
    if (this.config.showVolume) {
      this.drawVolume();
    }
    
    // Draw indicators (background)
    this.drawIndicators('background');
    
    // Draw candlesticks
    this.drawCandlesticks();
    
    // Draw indicators (overlay)
    this.drawIndicators('overlay');
    
    // Draw drawings
    this.drawDrawings();
    
    // Draw axes
    this.drawAxes();
  }
  
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    this.overlayCtx.clearRect(0, 0, this.width, this.height);
  }
  
  drawBackground() {
    const colors = this.colors[this.theme];
    
    this.ctx.fillStyle = colors.background;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }
  
  drawGrid() {
    const colors = this.colors[this.theme];
    const { padding } = this.config;
    
    this.ctx.strokeStyle = colors.grid;
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([2, 2]);
    
    // Horizontal grid lines (price levels)
    const priceSteps = 10;
    const priceStep = (this.priceRange.max - this.priceRange.min) / priceSteps;
    
    for (let i = 0; i <= priceSteps; i++) {
      const price = this.priceRange.min + (i * priceStep);
      const y = this.priceToY(price);
      
      this.ctx.beginPath();
      this.ctx.moveTo(padding.left, y);
      this.ctx.lineTo(this.width - padding.right, y);
      this.ctx.stroke();
    }
    
    // Vertical grid lines (time)
    const timeSteps = 8;
    const chartWidth = this.width - padding.left - padding.right;
    const timeStep = chartWidth / timeSteps;
    
    for (let i = 0; i <= timeSteps; i++) {
      const x = padding.left + (i * timeStep);
      
      this.ctx.beginPath();
      this.ctx.moveTo(x, padding.top);
      this.ctx.lineTo(x, this.height - padding.bottom);
      this.ctx.stroke();
    }
    
    this.ctx.setLineDash([]);
  }
  
  drawCandlesticks() {
    const colors = this.colors[this.theme];
    const { padding, candleWidth, candleSpacing } = this.config;
    
    const chartWidth = this.width - padding.left - padding.right;
    const candleAreaWidth = candleWidth + candleSpacing;
    const visibleCandles = Math.floor(chartWidth / candleAreaWidth);
    
    // Calculate visible range
    const startIndex = Math.max(0, this.data.length - visibleCandles + this.pan.x);
    const endIndex = Math.min(this.data.length, startIndex + visibleCandles);
    
    for (let i = startIndex; i < endIndex; i++) {
      const candle = this.data[i];
      const x = padding.left + ((i - startIndex) * candleAreaWidth) + (candleSpacing / 2);
      
      const openY = this.priceToY(candle.open);
      const closeY = this.priceToY(candle.close);
      const highY = this.priceToY(candle.high);
      const lowY = this.priceToY(candle.low);
      
      const isUp = candle.close >= candle.open;
      const bodyColor = isUp ? colors.upCandle : colors.downCandle;
      const wickColor = isUp ? colors.upWick : colors.downWick;
      
      // Draw wick
      this.ctx.strokeStyle = wickColor;
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(x + candleWidth / 2, highY);
      this.ctx.lineTo(x + candleWidth / 2, lowY);
      this.ctx.stroke();
      
      // Draw body
      const bodyHeight = Math.abs(closeY - openY);
      const bodyY = Math.min(openY, closeY);
      
      if (isUp) {
        this.ctx.strokeStyle = bodyColor;
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x, bodyY, candleWidth, bodyHeight || 1);
      } else {
        this.ctx.fillStyle = bodyColor;
        this.ctx.fillRect(x, bodyY, candleWidth, bodyHeight || 1);
      }
    }
  }
  
  drawVolume() {
    const colors = this.colors[this.theme];
    const { padding, candleWidth, candleSpacing } = this.config;
    
    const chartWidth = this.width - padding.left - padding.right;
    const chartHeight = this.height - padding.top - padding.bottom;
    const volumeHeight = chartHeight * this.config.volumeHeight;
    const volumeY = this.height - padding.bottom - volumeHeight;
    
    const candleAreaWidth = candleWidth + candleSpacing;
    const visibleCandles = Math.floor(chartWidth / candleAreaWidth);
    
    const startIndex = Math.max(0, this.data.length - visibleCandles + this.pan.x);
    const endIndex = Math.min(this.data.length, startIndex + visibleCandles);
    
    for (let i = startIndex; i < endIndex; i++) {
      const candle = this.data[i];
      const x = padding.left + ((i - startIndex) * candleAreaWidth) + (candleSpacing / 2);
      
      const volumeBarHeight = (candle.volume / this.volumeRange.max) * volumeHeight;
      const barY = volumeY + volumeHeight - volumeBarHeight;
      
      this.ctx.fillStyle = colors.volume;
      this.ctx.fillRect(x, barY, candleWidth, volumeBarHeight);
    }
  }
  
  drawIndicators(layer) {
    // Implementation for drawing indicators based on layer
    // This would render SMA, EMA, RSI, MACD, etc.
    
    for (const [indicatorId, indicator] of Object.entries(this.indicators)) {
      if (indicator.panel === 'main' && layer === 'overlay') {
        this.drawMainPanelIndicator(indicator);
      } else if (indicator.panel !== 'main' && layer === 'background') {
        this.drawSubPanelIndicator(indicator);
      }
    }
  }
  
  drawMainPanelIndicator(indicator) {
    if (!indicator.values || !indicator.values.length) return;
    
    const { padding, candleWidth, candleSpacing } = this.config;
    const chartWidth = this.width - padding.left - padding.right;
    const candleAreaWidth = candleWidth + candleSpacing;
    const visibleCandles = Math.floor(chartWidth / candleAreaWidth);
    
    const startIndex = Math.max(0, this.data.length - visibleCandles + this.pan.x);
    const endIndex = Math.min(this.data.length, startIndex + visibleCandles);
    
    this.ctx.strokeStyle = indicator.color || '#2962FF';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    
    let firstPoint = true;
    
    for (let i = startIndex; i < endIndex; i++) {
      if (i >= indicator.values.length) continue;
      
      const value = indicator.values[i];
      if (value === null || value === undefined || isNaN(value)) continue;
      
      const x = padding.left + ((i - startIndex) * candleAreaWidth) + candleWidth / 2;
      const y = this.priceToY(value);
      
      if (firstPoint) {
        this.ctx.moveTo(x, y);
        firstPoint = false;
      } else {
        this.ctx.lineTo(x, y);
      }
    }
    
    this.ctx.stroke();
  }
  
  drawSubPanelIndicator(indicator) {
    // Implementation for indicators in separate panels (RSI, MACD, etc.)
    // This would create sub-panels below the main chart
  }
  
  drawDrawings() {
    // Implementation for drawing tools
    for (const drawing of this.drawings) {
      this.drawSingleDrawing(drawing);
    }
  }
  
  drawSingleDrawing(drawing) {
    const colors = this.colors[this.theme];
    
    this.ctx.strokeStyle = drawing.style?.color || colors.text;
    this.ctx.lineWidth = drawing.style?.width || 2;
    
    switch (drawing.type) {
      case 'trend_line':
        this.drawTrendLine(drawing);
        break;
      case 'horizontal_line':
        this.drawHorizontalLine(drawing);
        break;
      case 'rectangle':
        this.drawRectangle(drawing);
        break;
      case 'fibonacci_retracement':
        this.drawFibonacci(drawing);
        break;
    }
  }
  
  drawTrendLine(drawing) {
    if (drawing.points.length < 2) return;
    
    const start = this.chartToCanvas(drawing.points[0]);
    const end = this.chartToCanvas(drawing.points[1]);
    
    this.ctx.beginPath();
    this.ctx.moveTo(start.x, start.y);
    this.ctx.lineTo(end.x, end.y);
    this.ctx.stroke();
  }
  
  drawHorizontalLine(drawing) {
    if (drawing.points.length < 1) return;
    
    const { padding } = this.config;
    const y = this.priceToY(drawing.points[0].price);
    
    this.ctx.beginPath();
    this.ctx.moveTo(padding.left, y);
    this.ctx.lineTo(this.width - padding.right, y);
    this.ctx.stroke();
  }
  
  drawRectangle(drawing) {
    if (drawing.points.length < 2) return;
    
    const start = this.chartToCanvas(drawing.points[0]);
    const end = this.chartToCanvas(drawing.points[1]);
    
    const width = end.x - start.x;
    const height = end.y - start.y;
    
    this.ctx.strokeRect(start.x, start.y, width, height);
  }
  
  drawFibonacci(drawing) {
    // Implementation for Fibonacci retracement levels
    if (drawing.points.length < 2) return;
    
    const start = this.chartToCanvas(drawing.points[0]);
    const end = this.chartToCanvas(drawing.points[1]);
    
    const fibLevels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
    const { padding } = this.config;
    
    for (const level of fibLevels) {
      const y = start.y + (end.y - start.y) * level;
      
      this.ctx.beginPath();
      this.ctx.moveTo(padding.left, y);
      this.ctx.lineTo(this.width - padding.right, y);
      this.ctx.stroke();
      
      // Draw level label
      this.ctx.fillStyle = this.colors[this.theme].text;
      this.ctx.font = '12px Arial';
      this.ctx.fillText(`${(level * 100).toFixed(1)}%`, this.width - padding.right + 5, y + 4);
    }
  }
  
  drawAxes() {
    this.drawPriceAxis();
    this.drawTimeAxis();
  }
  
  drawPriceAxis() {
    const colors = this.colors[this.theme];
    const { padding } = this.config;
    
    this.ctx.fillStyle = colors.text;
    this.ctx.font = '12px Arial';
    this.ctx.textAlign = 'left';
    
    const priceSteps = 10;
    const priceStep = (this.priceRange.max - this.priceRange.min) / priceSteps;
    
    for (let i = 0; i <= priceSteps; i++) {
      const price = this.priceRange.min + (i * priceStep);
      const y = this.priceToY(price);
      
      this.ctx.fillText(
        price.toFixed(2),
        this.width - padding.right + 5,
        y + 4
      );
    }
  }
  
  drawTimeAxis() {
    const colors = this.colors[this.theme];
    const { padding } = this.config;
    
    this.ctx.fillStyle = colors.text;
    this.ctx.font = '12px Arial';
    this.ctx.textAlign = 'center';
    
    const timeSteps = 6;
    const chartWidth = this.width - padding.left - padding.right;
    const timeStep = chartWidth / timeSteps;
    
    for (let i = 0; i <= timeSteps; i++) {
      const x = padding.left + (i * timeStep);
      const dataIndex = Math.floor((i / timeSteps) * this.data.length);
      
      if (dataIndex < this.data.length && this.data[dataIndex]) {
        const timestamp = this.data[dataIndex].timestamp;
        const date = new Date(timestamp);
        const timeString = date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        });
        
        this.ctx.fillText(timeString, x, this.height - padding.bottom + 20);
      }
    }
  }
  
  renderEmptyState() {
    const colors = this.colors[this.theme];
    
    this.ctx.fillStyle = colors.background;
    this.ctx.fillRect(0, 0, this.width, this.height);
    
    this.ctx.fillStyle = colors.text;
    this.ctx.font = '16px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText(
      'No chart data available',
      this.width / 2,
      this.height / 2
    );
  }
  
  // Utility methods
  priceToY(price) {
    const { padding } = this.config;
    const chartHeight = this.height - padding.top - padding.bottom - (this.config.showVolume ? this.height * this.config.volumeHeight : 0);
    const ratio = (price - this.priceRange.min) / (this.priceRange.max - this.priceRange.min);
    return padding.top + chartHeight * (1 - ratio);
  }
  
  yToPrice(y) {
    const { padding } = this.config;
    const chartHeight = this.height - padding.top - padding.bottom - (this.config.showVolume ? this.height * this.config.volumeHeight : 0);
    const ratio = 1 - (y - padding.top) / chartHeight;
    return this.priceRange.min + ratio * (this.priceRange.max - this.priceRange.min);
  }
  
  chartToCanvas(point) {
    const { padding, candleWidth, candleSpacing } = this.config;
    const candleAreaWidth = candleWidth + candleSpacing;
    
    // Convert timestamp to x coordinate
    const timeIndex = this.data.findIndex(d => d.timestamp >= point.timestamp);
    const x = padding.left + (timeIndex * candleAreaWidth) + candleWidth / 2;
    
    // Convert price to y coordinate
    const y = this.priceToY(point.price);
    
    return { x, y };
  }
  
  canvasToChartCoordinates(points) {
    return points.map(point => {
      const price = this.yToPrice(point.y);
      // Approximate timestamp based on x position
      const { padding, candleWidth, candleSpacing } = this.config;
      const candleAreaWidth = candleWidth + candleSpacing;
      const timeIndex = Math.floor((point.x - padding.left) / candleAreaWidth);
      const timestamp = this.data[timeIndex]?.timestamp || Date.now();
      
      return { timestamp, price };
    });
  }
  
  getDataPointAt(x, y) {
    const { padding, candleWidth, candleSpacing } = this.config;
    const candleAreaWidth = candleWidth + candleSpacing;
    const timeIndex = Math.floor((x - padding.left) / candleAreaWidth);
    
    if (timeIndex >= 0 && timeIndex < this.data.length) {
      return this.data[timeIndex];
    }
    
    return null;
  }
  
  addDataPoint(point) {
    this.data.push(point);
    this.calculatePriceRange();
    this.calculateVolumeRange();
  }
}

export default ChartRenderer;
export { ChartRenderer };