/**
 * GridWorks Chart Canvas Component
 * 
 * High-performance chart rendering using HTML5 Canvas with interactive features.
 * Supports zooming, panning, drawing tools, and real-time updates.
 */

import React, { useRef, useEffect, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import { ChartRenderer } from '../utils/ChartRenderer';
import { InteractionHandler } from '../utils/InteractionHandler';
import { DrawingTools } from '../utils/DrawingTools';

const ChartCanvas = forwardRef(({
  data = [],
  indicators = {},
  drawings = [],
  width = 800,
  height = 600,
  theme = 'dark',
  selectedTool = 'cursor',
  onDrawingAdd,
  onDrawingRemove,
  onDataPointClick,
  onZoomChange,
  onPanChange
}, ref) => {
  // Refs
  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const containerRef = useRef(null);
  
  // State
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentDrawing, setCurrentDrawing] = useState(null);
  const [zoom, setZoom] = useState({ x: 0, y: 0, scale: 1 });
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [crosshair, setCrosshair] = useState({ x: 0, y: 0, visible: false });
  const [tooltip, setTooltip] = useState({ visible: false, data: null, x: 0, y: 0 });
  
  // Instances
  const rendererRef = useRef(null);
  const interactionRef = useRef(null);
  const drawingToolsRef = useRef(null);
  
  // Initialize chart renderer
  useEffect(() => {
    if (!canvasRef.current || !overlayCanvasRef.current) return;
    
    rendererRef.current = new ChartRenderer({
      canvas: canvasRef.current,
      overlayCanvas: overlayCanvasRef.current,
      width,
      height,
      theme
    });
    
    interactionRef.current = new InteractionHandler({
      container: containerRef.current,
      canvas: canvasRef.current,
      onZoom: handleZoom,
      onPan: handlePan,
      onMouseMove: handleMouseMove,
      onClick: handleClick,
      onDrawStart: handleDrawStart,
      onDrawMove: handleDrawMove,
      onDrawEnd: handleDrawEnd
    });
    
    drawingToolsRef.current = new DrawingTools({
      canvas: overlayCanvasRef.current,
      theme
    });
    
    return () => {
      interactionRef.current?.cleanup();
    };
  }, [width, height, theme]);
  
  // Update chart data
  useEffect(() => {
    if (rendererRef.current && data.length > 0) {
      rendererRef.current.setData(data);
      rendererRef.current.setIndicators(indicators);
      rendererRef.current.setDrawings(drawings);
      rendererRef.current.render();
    }
  }, [data, indicators, drawings]);
  
  // Update theme
  useEffect(() => {
    if (rendererRef.current) {
      rendererRef.current.setTheme(theme);
      rendererRef.current.render();
    }
    if (drawingToolsRef.current) {
      drawingToolsRef.current.setTheme(theme);
    }
  }, [theme]);
  
  // Update drawing tool
  useEffect(() => {
    if (drawingToolsRef.current) {
      drawingToolsRef.current.setActiveTool(selectedTool);
    }
    if (interactionRef.current) {
      interactionRef.current.setMode(selectedTool === 'cursor' ? 'pan' : 'draw');
    }
  }, [selectedTool]);
  
  // Handle zoom
  const handleZoom = useCallback((zoomData) => {
    setZoom(zoomData);
    if (rendererRef.current) {
      rendererRef.current.setZoom(zoomData);
      rendererRef.current.render();
    }
    onZoomChange?.(zoomData);
  }, [onZoomChange]);
  
  // Handle pan
  const handlePan = useCallback((panData) => {
    setPan(panData);
    if (rendererRef.current) {
      rendererRef.current.setPan(panData);
      rendererRef.current.render();
    }
    onPanChange?.(panData);
  }, [onPanChange]);
  
  // Handle mouse move
  const handleMouseMove = useCallback((event) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    setCrosshair({ x, y, visible: true });
    
    // Update tooltip
    if (rendererRef.current) {
      const dataPoint = rendererRef.current.getDataPointAt(x, y);
      if (dataPoint) {
        setTooltip({
          visible: true,
          data: dataPoint,
          x: x + 10,
          y: y - 10
        });
      } else {
        setTooltip({ visible: false, data: null, x: 0, y: 0 });
      }
    }
    
    // Update overlay for drawing
    if (isDrawing && drawingToolsRef.current) {
      drawingToolsRef.current.updateCurrentDrawing(x, y);
    }
  }, [isDrawing]);
  
  // Handle click
  const handleClick = useCallback((event) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (rendererRef.current) {
      const dataPoint = rendererRef.current.getDataPointAt(x, y);
      onDataPointClick?.(dataPoint, { x, y });
    }
  }, [onDataPointClick]);
  
  // Handle drawing start
  const handleDrawStart = useCallback((event) => {
    if (selectedTool === 'cursor') return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (drawingToolsRef.current) {
      const drawing = drawingToolsRef.current.startDrawing(selectedTool, x, y);
      setCurrentDrawing(drawing);
      setIsDrawing(true);
    }
  }, [selectedTool]);
  
  // Handle drawing move
  const handleDrawMove = useCallback((event) => {
    if (!isDrawing || !drawingToolsRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    drawingToolsRef.current.updateDrawing(x, y);
  }, [isDrawing]);
  
  // Handle drawing end
  const handleDrawEnd = useCallback((event) => {
    if (!isDrawing || !drawingToolsRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const completedDrawing = drawingToolsRef.current.endDrawing(x, y);
    
    if (completedDrawing && onDrawingAdd) {
      // Convert canvas coordinates to chart coordinates
      const chartPoints = rendererRef.current.canvasToChartCoordinates(completedDrawing.points);
      onDrawingAdd(selectedTool, chartPoints, completedDrawing.style);
    }
    
    setCurrentDrawing(null);
    setIsDrawing(false);
  }, [isDrawing, selectedTool, onDrawingAdd]);
  
  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    // Chart operations
    render: () => rendererRef.current?.render(),
    clear: () => rendererRef.current?.clear(),
    
    // Data operations
    addDataPoint: (point) => {
      if (rendererRef.current) {
        rendererRef.current.addDataPoint(point);
        rendererRef.current.render();
      }
    },
    
    // View operations
    zoomIn: () => {
      const newZoom = { ...zoom, scale: zoom.scale * 1.2 };
      handleZoom(newZoom);
    },
    zoomOut: () => {
      const newZoom = { ...zoom, scale: zoom.scale * 0.8 };
      handleZoom(newZoom);
    },
    resetZoom: () => {
      const resetZoom = { x: 0, y: 0, scale: 1 };
      handleZoom(resetZoom);
    },
    
    // Export operations
    exportAsImage: (format = 'png') => {
      return canvasRef.current?.toDataURL(`image/${format}`);
    },
    
    // Drawing operations
    clearDrawings: () => {
      if (drawingToolsRef.current) {
        drawingToolsRef.current.clearAll();
      }
    },
    
    // Get chart state
    getViewport: () => ({ zoom, pan }),
    getCanvasSize: () => ({ width, height })
  }), [zoom, pan, handleZoom, width, height]);
  
  return (
    <div 
      ref={containerRef}
      className="chart-canvas-container"
      style={{ 
        position: 'relative', 
        width, 
        height,
        cursor: selectedTool === 'cursor' ? 'default' : 'crosshair'
      }}
    >
      {/* Main chart canvas */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          zIndex: 1
        }}
      />
      
      {/* Overlay canvas for drawings and interactions */}
      <canvas
        ref={overlayCanvasRef}
        width={width}
        height={height}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          zIndex: 2,
          pointerEvents: 'none'
        }}
      />
      
      {/* Crosshair */}
      {crosshair.visible && (
        <div
          className="chart-crosshair"
          style={{
            position: 'absolute',
            left: crosshair.x,
            top: crosshair.y,
            width: 1,
            height: 1,
            pointerEvents: 'none',
            zIndex: 3
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: -width / 2,
              width: width,
              height: 1,
              backgroundColor: theme === 'dark' ? '#666' : '#ccc',
              opacity: 0.5
            }}
          />
          <div
            style={{
              position: 'absolute',
              top: -height / 2,
              width: 1,
              height: height,
              backgroundColor: theme === 'dark' ? '#666' : '#ccc',
              opacity: 0.5
            }}
          />
        </div>
      )}
      
      {/* Tooltip */}
      {tooltip.visible && tooltip.data && (
        <div
          className="chart-tooltip"
          style={{
            position: 'absolute',
            left: tooltip.x,
            top: tooltip.y,
            backgroundColor: theme === 'dark' ? '#333' : '#fff',
            color: theme === 'dark' ? '#fff' : '#333',
            border: `1px solid ${theme === 'dark' ? '#555' : '#ddd'}`,
            borderRadius: 4,
            padding: 8,
            fontSize: 12,
            pointerEvents: 'none',
            zIndex: 4,
            minWidth: 120
          }}
        >
          <div>Time: {new Date(tooltip.data.timestamp).toLocaleString()}</div>
          <div>Open: {tooltip.data.open?.toFixed(2)}</div>
          <div>High: {tooltip.data.high?.toFixed(2)}</div>
          <div>Low: {tooltip.data.low?.toFixed(2)}</div>
          <div>Close: {tooltip.data.close?.toFixed(2)}</div>
          <div>Volume: {tooltip.data.volume?.toLocaleString()}</div>
        </div>
      )}
      
      {/* Drawing indicator */}
      {isDrawing && (
        <div
          className="drawing-indicator"
          style={{
            position: 'absolute',
            top: 10,
            left: 10,
            backgroundColor: theme === 'dark' ? '#333' : '#fff',
            color: theme === 'dark' ? '#fff' : '#333',
            padding: '4px 8px',
            borderRadius: 4,
            fontSize: 12,
            zIndex: 5
          }}
        >
          Drawing: {selectedTool.replace('_', ' ')}
        </div>
      )}
    </div>
  );
});

ChartCanvas.displayName = 'ChartCanvas';

export default ChartCanvas;
export { ChartCanvas };