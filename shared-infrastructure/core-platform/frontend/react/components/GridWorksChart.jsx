/**
 * GridWorks Professional Chart Component
 * 
 * React component for displaying interactive financial charts with AI features.
 * Integrates with GridWorks charting API for real-time data and analysis.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChartingAPI } from '../services/ChartingAPI';
import { WebSocketClient } from '../services/WebSocketClient';
import { VoiceCommands } from '../services/VoiceCommands';
import { ChartCanvas } from './ChartCanvas';
import { ChartToolbar } from './ChartToolbar';
import { IndicatorPanel } from './IndicatorPanel';
import { DrawingToolsPanel } from './DrawingToolsPanel';
import { PatternAlert } from './PatternAlert';
import './GridWorksChart.css';

const GridWorksChart = ({
  symbol,
  timeframe = '5m',
  theme = 'dark',
  width = 800,
  height = 600,
  enableVoiceCommands = true,
  enablePatternDetection = true,
  enableDrawingTools = true,
  enableIndicators = true,
  onPatternDetected = null,
  onVoiceCommand = null,
  onChartUpdate = null,
  userId,
  authToken
}) => {
  // State management
  const [sessionId, setSessionId] = useState(null);
  const [chartId, setChartId] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [indicators, setIndicators] = useState({});
  const [drawings, setDrawings] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTool, setSelectedTool] = useState('cursor');
  const [isVoiceActive, setIsVoiceActive] = useState(false);

  // Refs
  const chartRef = useRef(null);
  const wsClientRef = useRef(null);
  const voiceCommandsRef = useRef(null);
  const apiRef = useRef(null);

  // Initialize API client
  useEffect(() => {
    if (authToken) {
      apiRef.current = new ChartingAPI({
        baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
        authToken
      });
    }
  }, [authToken]);

  // Initialize chart session
  useEffect(() => {
    const initializeChart = async () => {
      if (!apiRef.current) return;

      try {
        setIsLoading(true);
        setError(null);

        // Create session
        const session = await apiRef.current.createSession({
          theme,
          default_timeframe: timeframe
        });
        setSessionId(session.session_id);

        // Create chart
        const chart = await apiRef.current.createChart(session.session_id, {
          symbol,
          chart_type: 'candlestick',
          timeframe,
          theme,
          show_volume: true,
          enable_ai_patterns: enablePatternDetection,
          enable_voice_commands: enableVoiceCommands
        });
        setChartId(chart.chart_id);

        // Load initial data
        const data = await apiRef.current.getChartData(chart.chart_id);
        setChartData(data.data || []);
        setIndicators(data.indicators || {});
        setDrawings(data.drawings || []);
        setPatterns(data.patterns || []);

        // Initialize WebSocket
        if (session.session_id) {
          initializeWebSocket(session.session_id);
        }

        // Initialize voice commands
        if (enableVoiceCommands) {
          initializeVoiceCommands(session.session_id);
        }

        setIsLoading(false);
      } catch (err) {
        console.error('Chart initialization error:', err);
        setError(err.message);
        setIsLoading(false);
      }
    };

    initializeChart();

    // Cleanup
    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
      }
      if (voiceCommandsRef.current) {
        voiceCommandsRef.current.stop();
      }
    };
  }, [symbol, timeframe, theme, enablePatternDetection, enableVoiceCommands]);

  // Initialize WebSocket connection
  const initializeWebSocket = useCallback((sessionId) => {
    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/api/v1/charting/ws/${sessionId}`;
    
    wsClientRef.current = new WebSocketClient(wsUrl);
    
    wsClientRef.current.onMessage = (data) => {
      switch (data.type) {
        case 'data_update':
          if (data.symbol === symbol) {
            setChartData(prev => [...prev, data.data]);
            onChartUpdate?.(data.data);
          }
          break;
          
        case 'pattern_detected':
          setPatterns(prev => [...prev, data.pattern]);
          onPatternDetected?.(data.pattern);
          break;
          
        case 'indicator_update':
          setIndicators(prev => ({
            ...prev,
            [data.indicator_id]: data.values
          }));
          break;
          
        case 'drawing_update':
          setDrawings(prev => [...prev, data.drawing]);
          break;
      }
    };
    
    wsClientRef.current.connect();
    
    // Subscribe to symbol
    wsClientRef.current.subscribe([symbol]);
  }, [symbol, onChartUpdate, onPatternDetected]);

  // Initialize voice commands
  const initializeVoiceCommands = useCallback((sessionId) => {
    if (!enableVoiceCommands) return;
    
    voiceCommandsRef.current = new VoiceCommands({
      onCommand: async (command) => {
        try {
          setIsVoiceActive(true);
          const result = await apiRef.current.executeVoiceCommand(sessionId, command);
          onVoiceCommand?.(command, result);
          
          // Refresh chart data after voice command
          if (result.success && chartId) {
            const data = await apiRef.current.getChartData(chartId);
            setChartData(data.data || []);
            setIndicators(data.indicators || {});
            setDrawings(data.drawings || []);
          }
        } catch (err) {
          console.error('Voice command error:', err);
        } finally {
          setIsVoiceActive(false);
        }
      },
      language: 'en-US' // Can be configured
    });
  }, [enableVoiceCommands, chartId, onVoiceCommand]);

  // Add indicator
  const addIndicator = useCallback(async (indicatorType, params = {}) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      const indicator = await apiRef.current.addIndicator(chartId, {
        indicator_type: indicatorType,
        params,
        color: params.color || '#2962FF',
        panel: params.panel || 'main'
      });
      
      // Refresh indicators
      const data = await apiRef.current.getChartData(chartId);
      setIndicators(data.indicators || {});
      
      return indicator;
    } catch (err) {
      console.error('Add indicator error:', err);
      throw err;
    }
  }, [chartId]);

  // Remove indicator
  const removeIndicator = useCallback(async (indicatorId) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      await apiRef.current.removeIndicator(chartId, indicatorId);
      
      // Update local state
      setIndicators(prev => {
        const updated = { ...prev };
        delete updated[indicatorId];
        return updated;
      });
    } catch (err) {
      console.error('Remove indicator error:', err);
      throw err;
    }
  }, [chartId]);

  // Add drawing
  const addDrawing = useCallback(async (drawingType, points, style = {}) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      const drawing = await apiRef.current.addDrawing(chartId, {
        drawing_type: drawingType,
        points,
        style: {
          color: '#2962FF',
          width: 2,
          style: 'solid',
          ...style
        }
      });
      
      // Update local state
      setDrawings(prev => [...prev, drawing]);
      
      return drawing;
    } catch (err) {
      console.error('Add drawing error:', err);
      throw err;
    }
  }, [chartId]);

  // Remove drawing
  const removeDrawing = useCallback(async (drawingId) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      await apiRef.current.removeDrawing(chartId, drawingId);
      
      // Update local state
      setDrawings(prev => prev.filter(d => d.drawing_id !== drawingId));
    } catch (err) {
      console.error('Remove drawing error:', err);
      throw err;
    }
  }, [chartId]);

  // Share chart
  const shareChart = useCallback(async (options = {}) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      const shareData = await apiRef.current.shareChart(chartId, {
        include_image: true,
        analysis_notes: options.notes,
        visibility: options.visibility || 'public'
      });
      
      return shareData;
    } catch (err) {
      console.error('Share chart error:', err);
      throw err;
    }
  }, [chartId]);

  // Voice command toggle
  const toggleVoiceCommands = useCallback(() => {
    if (!voiceCommandsRef.current) return;
    
    if (isVoiceActive) {
      voiceCommandsRef.current.stop();
      setIsVoiceActive(false);
    } else {
      voiceCommandsRef.current.start();
      setIsVoiceActive(true);
    }
  }, [isVoiceActive]);

  // Change timeframe
  const changeTimeframe = useCallback(async (newTimeframe) => {
    if (!sessionId || !apiRef.current) return;
    
    try {
      // Create new chart with different timeframe
      const chart = await apiRef.current.createChart(sessionId, {
        symbol,
        chart_type: 'candlestick',
        timeframe: newTimeframe,
        theme,
        show_volume: true,
        enable_ai_patterns: enablePatternDetection,
        enable_voice_commands: enableVoiceCommands
      });
      
      setChartId(chart.chart_id);
      
      // Load new data
      const data = await apiRef.current.getChartData(chart.chart_id);
      setChartData(data.data || []);
      setIndicators(data.indicators || {});
      setDrawings(data.drawings || []);
    } catch (err) {
      console.error('Change timeframe error:', err);
    }
  }, [sessionId, symbol, theme, enablePatternDetection, enableVoiceCommands]);

  // Error display
  if (error) {
    return (
      <div className="gridworks-chart-error">
        <h3>Chart Error</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  // Loading display
  if (isLoading) {
    return (
      <div className="gridworks-chart-loading">
        <div className="loading-spinner"></div>
        <p>Loading GridWorks Chart...</p>
      </div>
    );
  }

  return (
    <div 
      className={`gridworks-chart ${theme}`} 
      style={{ width, height }}
    >
      {/* Chart Toolbar */}
      <ChartToolbar
        symbol={symbol}
        timeframe={timeframe}
        onTimeframeChange={changeTimeframe}
        onShareChart={shareChart}
        onVoiceToggle={enableVoiceCommands ? toggleVoiceCommands : null}
        isVoiceActive={isVoiceActive}
        selectedTool={selectedTool}
        onToolSelect={setSelectedTool}
      />

      {/* Main Chart Area */}
      <div className="chart-container">
        {/* Chart Canvas */}
        <ChartCanvas
          ref={chartRef}
          data={chartData}
          indicators={indicators}
          drawings={drawings}
          width={width}
          height={height - 60} // Account for toolbar
          theme={theme}
          selectedTool={selectedTool}
          onDrawingAdd={addDrawing}
          onDrawingRemove={removeDrawing}
        />

        {/* Side Panels */}
        <div className="chart-panels">
          {/* Indicators Panel */}
          {enableIndicators && (
            <IndicatorPanel
              indicators={indicators}
              onAddIndicator={addIndicator}
              onRemoveIndicator={removeIndicator}
              theme={theme}
            />
          )}

          {/* Drawing Tools Panel */}
          {enableDrawingTools && (
            <DrawingToolsPanel
              selectedTool={selectedTool}
              onToolSelect={setSelectedTool}
              drawings={drawings}
              onRemoveDrawing={removeDrawing}
              theme={theme}
            />
          )}
        </div>
      </div>

      {/* Pattern Alerts */}
      {enablePatternDetection && patterns.length > 0 && (
        <PatternAlert
          patterns={patterns}
          onDismiss={(patternId) => {
            setPatterns(prev => prev.filter(p => p.id !== patternId));
          }}
          theme={theme}
        />
      )}

      {/* Voice Command Indicator */}
      {enableVoiceCommands && isVoiceActive && (
        <div className="voice-indicator">
          <div className="voice-pulse"></div>
          <span>Listening for voice commands...</span>
        </div>
      )}
    </div>
  );
};

export default GridWorksChart;
export { GridWorksChart };

// Export hook for easier usage
export const useGridWorksChart = (symbol, options = {}) => {
  const [chart, setChart] = useState(null);
  const chartRef = useRef(null);

  const initChart = useCallback((container) => {
    if (container && !chart) {
      const chartInstance = new GridWorksChart({
        symbol,
        ...options
      });
      setChart(chartInstance);
      chartRef.current = chartInstance;
    }
  }, [symbol, options, chart]);

  return {
    chart: chartRef.current,
    initChart,
    addIndicator: chartRef.current?.addIndicator,
    removeIndicator: chartRef.current?.removeIndicator,
    addDrawing: chartRef.current?.addDrawing,
    shareChart: chartRef.current?.shareChart
  };
};