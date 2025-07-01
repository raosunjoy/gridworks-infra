/**
 * GridWorks Mobile Chart View
 * 
 * React Native component for displaying interactive financial charts.
 * Optimized for touch gestures and mobile performance.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  StyleSheet,
  Dimensions,
  PanGestureHandler,
  PinchGestureHandler,
  TapGestureHandler,
  State,
  GestureHandlerRootView
} from 'react-native';
import { Canvas, useCanvasRef } from '@shopify/react-native-skia';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ChartingAPI } from '../services/ChartingAPI';
import { MobileWebSocketClient } from '../services/MobileWebSocketClient';
import { MobileVoiceCommands } from '../services/MobileVoiceCommands';
import { MobileChartRenderer } from '../utils/MobileChartRenderer';
import { ChartToolbar } from './ChartToolbar';
import { IndicatorModal } from './IndicatorModal';
import { DrawingToolsModal } from './DrawingToolsModal';
import { PatternAlert } from './PatternAlert';

interface GridWorksChartViewProps {
  symbol: string;
  timeframe?: string;
  theme?: 'dark' | 'light';
  enableVoiceCommands?: boolean;
  enablePatternDetection?: boolean;
  enableDrawingTools?: boolean;
  enableIndicators?: boolean;
  onPatternDetected?: (pattern: any) => void;
  onVoiceCommand?: (command: string, result: any) => void;
  onChartUpdate?: (data: any) => void;
  userId: string;
  authToken: string;
  style?: any;
}

const GridWorksChartView: React.FC<GridWorksChartViewProps> = ({
  symbol,
  timeframe = '5m',
  theme = 'dark',
  enableVoiceCommands = true,
  enablePatternDetection = true,
  enableDrawingTools = true,
  enableIndicators = true,
  onPatternDetected,
  onVoiceCommand,
  onChartUpdate,
  userId,
  authToken,
  style
}) => {
  // Get screen dimensions
  const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
  const insets = useSafeAreaInsets();
  
  // Chart dimensions
  const chartWidth = screenWidth;
  const chartHeight = screenHeight - insets.top - insets.bottom - 120; // Account for toolbar
  
  // State management
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [chartId, setChartId] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [indicators, setIndicators] = useState<any>({});
  const [drawings, setDrawings] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [showIndicators, setShowIndicators] = useState(false);
  const [showDrawingTools, setShowDrawingTools] = useState(false);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [selectedTool, setSelectedTool] = useState('cursor');
  
  // Gesture state
  const [scale, setScale] = useState(1);
  const [translateX, setTranslateX] = useState(0);
  const [translateY, setTranslateY] = useState(0);
  const [lastScale, setLastScale] = useState(1);
  const [lastTranslateX, setLastTranslateX] = useState(0);
  const [lastTranslateY, setLastTranslateY] = useState(0);
  
  // Refs
  const canvasRef = useCanvasRef();
  const panRef = useRef<PanGestureHandler>(null);
  const pinchRef = useRef<PinchGestureHandler>(null);
  const tapRef = useRef<TapGestureHandler>(null);
  const apiRef = useRef<ChartingAPI | null>(null);
  const wsClientRef = useRef<MobileWebSocketClient | null>(null);
  const voiceCommandsRef = useRef<MobileVoiceCommands | null>(null);
  const rendererRef = useRef<MobileChartRenderer | null>(null);
  
  // Initialize API client
  useEffect(() => {
    if (authToken) {
      apiRef.current = new ChartingAPI({
        baseURL: __DEV__ ? 'http://localhost:8000' : 'https://api.gridworks.ai',
        authToken
      });
    }
  }, [authToken]);
  
  // Initialize chart
  useEffect(() => {
    initializeChart();
    
    return () => {
      cleanup();
    };
  }, [symbol, timeframe]);
  
  // Initialize chart renderer
  useEffect(() => {
    if (canvasRef.current) {
      rendererRef.current = new MobileChartRenderer({
        canvas: canvasRef.current,
        width: chartWidth,
        height: chartHeight,
        theme
      });
    }
  }, [chartWidth, chartHeight, theme]);
  
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
      initializeWebSocket(session.session_id);
      
      // Initialize voice commands
      if (enableVoiceCommands) {
        initializeVoiceCommands(session.session_id);
      }
      
      setIsLoading(false);
    } catch (err: any) {
      console.error('Chart initialization error:', err);
      setError(err.message);
      setIsLoading(false);
    }
  };
  
  const initializeWebSocket = (sessionId: string) => {
    const wsUrl = `${__DEV__ ? 'ws://localhost:8000' : 'wss://api.gridworks.ai'}/api/v1/charting/ws/${sessionId}`;
    
    wsClientRef.current = new MobileWebSocketClient(wsUrl);
    
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
      }
    };
    
    wsClientRef.current.connect();
    wsClientRef.current.subscribe([symbol]);
  };
  
  const initializeVoiceCommands = (sessionId: string) => {
    voiceCommandsRef.current = new MobileVoiceCommands({
      onCommand: async (command: string) => {
        try {
          setIsVoiceActive(true);
          const result = await apiRef.current?.executeVoiceCommand(sessionId, command);
          onVoiceCommand?.(command, result);
          
          // Refresh chart data after voice command
          if (result?.success && chartId) {
            const data = await apiRef.current?.getChartData(chartId);
            if (data) {
              setChartData(data.data || []);
              setIndicators(data.indicators || {});
              setDrawings(data.drawings || []);
            }
          }
        } catch (err) {
          console.error('Voice command error:', err);
        } finally {
          setIsVoiceActive(false);
        }
      }
    });
  };
  
  const cleanup = () => {
    wsClientRef.current?.disconnect();
    voiceCommandsRef.current?.stop();
  };
  
  // Gesture handlers
  const onPanGestureEvent = useCallback((event: any) => {
    if (selectedTool !== 'cursor') return;
    
    const { translationX, translationY } = event.nativeEvent;
    setTranslateX(lastTranslateX + translationX);
    setTranslateY(lastTranslateY + translationY);
  }, [selectedTool, lastTranslateX, lastTranslateY]);
  
  const onPanStateChange = useCallback((event: any) => {
    if (event.nativeEvent.state === State.END) {
      setLastTranslateX(translateX);
      setLastTranslateY(translateY);
    }
  }, [translateX, translateY]);
  
  const onPinchGestureEvent = useCallback((event: any) => {
    const { scale: gestureScale } = event.nativeEvent;
    setScale(lastScale * gestureScale);
  }, [lastScale]);
  
  const onPinchStateChange = useCallback((event: any) => {
    if (event.nativeEvent.state === State.END) {
      setLastScale(scale);
    }
  }, [scale]);
  
  const onTapGestureEvent = useCallback((event: any) => {
    const { x, y } = event.nativeEvent;
    
    if (rendererRef.current) {
      const dataPoint = rendererRef.current.getDataPointAt(x, y);
      if (dataPoint) {
        // Handle data point selection
        console.log('Selected data point:', dataPoint);
      }
    }
  }, []);
  
  // Chart operations
  const addIndicator = async (indicatorType: string, params: any = {}) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      await apiRef.current.addIndicator(chartId, {
        indicator_type: indicatorType,
        params,
        color: params.color || '#2962FF',
        panel: params.panel || 'main'
      });
      
      // Refresh indicators
      const data = await apiRef.current.getChartData(chartId);
      setIndicators(data.indicators || {});
    } catch (err) {
      console.error('Add indicator error:', err);
    }
  };
  
  const addDrawing = async (drawingType: string, points: any[], style: any = {}) => {
    if (!chartId || !apiRef.current) return;
    
    try {
      await apiRef.current.addDrawing(chartId, {
        drawing_type: drawingType,
        points,
        style: {
          color: '#2962FF',
          width: 2,
          style: 'solid',
          ...style
        }
      });
      
      // Refresh drawings
      const data = await apiRef.current.getChartData(chartId);
      setDrawings(data.drawings || []);
    } catch (err) {
      console.error('Add drawing error:', err);
    }
  };
  
  const shareChart = async () => {
    if (!chartId || !apiRef.current) return;
    
    try {
      const shareData = await apiRef.current.shareChart(chartId, {
        include_image: true,
        visibility: 'public'
      });
      
      // Handle share data (open share sheet, etc.)
      console.log('Chart shared:', shareData);
    } catch (err) {
      console.error('Share chart error:', err);
    }
  };
  
  const toggleVoiceCommands = () => {
    if (!voiceCommandsRef.current) return;
    
    if (isVoiceActive) {
      voiceCommandsRef.current.stop();
      setIsVoiceActive(false);
    } else {
      voiceCommandsRef.current.start();
      setIsVoiceActive(true);
    }
  };
  
  // Render chart data
  useEffect(() => {
    if (rendererRef.current && chartData.length > 0) {
      rendererRef.current.setData(chartData);
      rendererRef.current.setIndicators(indicators);
      rendererRef.current.setDrawings(drawings);
      rendererRef.current.setTransform({ scale, translateX, translateY });
      rendererRef.current.render();
    }
  }, [chartData, indicators, drawings, scale, translateX, translateY]);
  
  if (error) {
    return (
      <View style={[styles.container, styles.errorContainer]}>
        <Text style={styles.errorText}>Chart Error: {error}</Text>
      </View>
    );
  }
  
  if (isLoading) {
    return (
      <View style={[styles.container, styles.loadingContainer]}>
        <Text style={styles.loadingText}>Loading GridWorks Chart...</Text>
      </View>
    );
  }
  
  return (
    <GestureHandlerRootView style={[styles.container, style]}>
      <View style={styles.chartContainer}>
        {/* Chart Toolbar */}
        <ChartToolbar
          symbol={symbol}
          timeframe={timeframe}
          theme={theme}
          onIndicatorsPress={() => setShowIndicators(true)}
          onDrawingToolsPress={() => setShowDrawingTools(true)}
          onVoiceToggle={enableVoiceCommands ? toggleVoiceCommands : undefined}
          onSharePress={shareChart}
          isVoiceActive={isVoiceActive}
        />
        
        {/* Chart Canvas with Gestures */}
        <PanGestureHandler
          ref={panRef}
          onGestureEvent={onPanGestureEvent}
          onHandlerStateChange={onPanStateChange}
          simultaneousHandlers={[pinchRef]}
        >
          <PinchGestureHandler
            ref={pinchRef}
            onGestureEvent={onPinchGestureEvent}
            onHandlerStateChange={onPinchStateChange}
            simultaneousHandlers={[panRef]}
          >
            <TapGestureHandler
              ref={tapRef}
              onGestureEvent={onTapGestureEvent}
            >
              <View style={styles.canvasContainer}>
                <Canvas
                  ref={canvasRef}
                  style={{ width: chartWidth, height: chartHeight }}
                />
              </View>
            </TapGestureHandler>
          </PinchGestureHandler>
        </PanGestureHandler>
      </View>
      
      {/* Modals */}
      <IndicatorModal
        visible={showIndicators}
        onClose={() => setShowIndicators(false)}
        onAddIndicator={addIndicator}
        indicators={indicators}
        theme={theme}
      />
      
      <DrawingToolsModal
        visible={showDrawingTools}
        onClose={() => setShowDrawingTools(false)}
        onSelectTool={setSelectedTool}
        selectedTool={selectedTool}
        theme={theme}
      />
      
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
      
      {/* Voice Indicator */}
      {enableVoiceCommands && isVoiceActive && (
        <View style={styles.voiceIndicator}>
          <Text style={styles.voiceText}>🎤 Listening...</Text>
        </View>
      )}
    </GestureHandlerRootView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a'
  },
  chartContainer: {
    flex: 1
  },
  canvasContainer: {
    flex: 1
  },
  errorContainer: {
    justifyContent: 'center',
    alignItems: 'center'
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 16,
    textAlign: 'center'
  },
  loadingContainer: {
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {
    color: '#fff',
    fontSize: 16
  },
  voiceIndicator: {
    position: 'absolute',
    top: 100,
    left: 20,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    padding: 10,
    borderRadius: 20,
    flexDirection: 'row',
    alignItems: 'center'
  },
  voiceText: {
    color: '#fff',
    fontSize: 14,
    marginLeft: 5
  }
});

export default GridWorksChartView;
export { GridWorksChartView };