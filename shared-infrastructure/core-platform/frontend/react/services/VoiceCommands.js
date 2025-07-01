/**
 * GridWorks Voice Commands Service
 * 
 * Handles speech recognition and natural language processing for chart commands.
 * Supports multiple languages and provides intelligent command interpretation.
 */

class VoiceCommands {
  constructor({ onCommand, language = 'en-US', continuous = false }) {
    this.onCommand = onCommand;
    this.language = language;
    this.continuous = continuous;
    
    this.recognition = null;
    this.isListening = false;
    this.isSupported = this.checkSupport();
    
    // Command patterns for natural language processing
    this.commandPatterns = {
      // Indicators
      addIndicator: [
        /add (\w+)( \d+)?( day| period)?( moving average| ma)?/i,
        /show (\w+)( indicator)?/i,
        /(sma|ema|rsi|macd|bollinger|bands) (\d+)?/i
      ],
      
      // Drawing tools
      addDrawing: [
        /draw (trend line|trendline|line|support|resistance)( at \d+)?/i,
        /(fibonacci|fib)( retracement)?/i,
        /add (rectangle|ellipse|arrow)/i
      ],
      
      // Timeframe changes
      changeTimeframe: [
        /(change|switch) to (\w+)( timeframe| interval)?/i,
        /(\d+)(m|h|d)( chart| timeframe)?/i,
        /(one|five|fifteen|thirty) minute/i,
        /(hourly|daily|weekly|monthly)/i
      ],
      
      // Symbol changes
      changeSymbol: [
        /(show|display|chart) (\w+)/i,
        /(switch|change) to (\w+)/i
      ],
      
      // Pattern detection
      findPatterns: [
        /(show|find|detect) (patterns|bullish|bearish)/i,
        /(head and shoulders|double top|double bottom|triangle)/i
      ],
      
      // Layout changes
      changeLayout: [
        /(switch|change) to (single|split|grid)( layout)?/i,
        /(show|display) (\d+) charts/i
      ]
    };
    
    this.init();
  }

  checkSupport() {
    return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  }

  init() {
    if (!this.isSupported) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    this.recognition.lang = this.language;
    this.recognition.continuous = this.continuous;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    
    this.recognition.onstart = () => {
      console.log('Voice recognition started');
      this.isListening = true;
    };
    
    this.recognition.onend = () => {
      console.log('Voice recognition ended');
      this.isListening = false;
    };
    
    this.recognition.onerror = (event) => {
      console.error('Voice recognition error:', event.error);
      this.isListening = false;
    };
    
    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.toLowerCase().trim();
      console.log('Voice command received:', transcript);
      
      this.processCommand(transcript);
    };
  }

  start() {
    if (!this.isSupported || !this.recognition) {
      console.warn('Speech recognition not available');
      return false;
    }
    
    if (this.isListening) {
      return true;
    }
    
    try {
      this.recognition.start();
      return true;
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      return false;
    }
  }

  stop() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  processCommand(transcript) {
    const command = this.parseCommand(transcript);
    
    if (command) {
      this.onCommand?.(command);
    } else {
      console.log('Command not recognized:', transcript);
      // Still send raw transcript for potential backend processing
      this.onCommand?.(transcript);
    }
  }

  parseCommand(transcript) {
    // Try to match against known patterns
    for (const [action, patterns] of Object.entries(this.commandPatterns)) {
      for (const pattern of patterns) {
        const match = transcript.match(pattern);
        if (match) {
          return this.buildCommand(action, match, transcript);
        }
      }
    }
    
    return null;
  }

  buildCommand(action, match, originalText) {
    switch (action) {
      case 'addIndicator':
        return this.buildIndicatorCommand(match, originalText);
        
      case 'addDrawing':
        return this.buildDrawingCommand(match, originalText);
        
      case 'changeTimeframe':
        return this.buildTimeframeCommand(match, originalText);
        
      case 'changeSymbol':
        return this.buildSymbolCommand(match, originalText);
        
      case 'findPatterns':
        return this.buildPatternCommand(match, originalText);
        
      case 'changeLayout':
        return this.buildLayoutCommand(match, originalText);
        
      default:
        return originalText;
    }
  }

  buildIndicatorCommand(match, originalText) {
    const indicatorType = match[1]?.toUpperCase();
    const period = match[2] ? parseInt(match[2]) : null;
    
    // Map common names to technical names
    const indicatorMap = {
      'MOVING': 'SMA',
      'SIMPLE': 'SMA',
      'EXPONENTIAL': 'EMA',
      'RELATIVE': 'RSI',
      'STRENGTH': 'RSI',
      'BOLLINGER': 'BOLLINGER_BANDS',
      'BANDS': 'BOLLINGER_BANDS'
    };
    
    const mappedIndicator = indicatorMap[indicatorType] || indicatorType;
    
    return {
      action: 'add_indicator',
      indicator_type: mappedIndicator,
      params: period ? { period } : {},
      original: originalText
    };
  }

  buildDrawingCommand(match, originalText) {
    const drawingType = match[1]?.toLowerCase().replace(/\s+/g, '_');
    const price = match[2] ? parseFloat(match[2]) : null;
    
    return {
      action: 'add_drawing',
      drawing_type: drawingType,
      params: price ? { price } : {},
      original: originalText
    };
  }

  buildTimeframeCommand(match, originalText) {
    let timeframe = null;
    
    // Extract timeframe from various formats
    if (match[2]) {
      timeframe = match[2].toLowerCase();
    } else if (match[1] && match[2]) {
      timeframe = `${match[1]}${match[2]}`;
    }
    
    // Map natural language to timeframe codes
    const timeframeMap = {
      'one': '1m',
      'five': '5m',
      'fifteen': '15m',
      'thirty': '30m',
      'hourly': '1h',
      'daily': '1d',
      'weekly': '1w',
      'monthly': '1M'
    };
    
    timeframe = timeframeMap[timeframe] || timeframe;
    
    return {
      action: 'change_timeframe',
      timeframe,
      original: originalText
    };
  }

  buildSymbolCommand(match, originalText) {
    const symbol = match[2]?.toUpperCase();
    
    return {
      action: 'change_symbol',
      symbol,
      original: originalText
    };
  }

  buildPatternCommand(match, originalText) {
    const patternType = match[2]?.toLowerCase();
    
    return {
      action: 'detect_patterns',
      pattern_type: patternType,
      original: originalText
    };
  }

  buildLayoutCommand(match, originalText) {
    const layoutType = match[2]?.toLowerCase();
    const chartCount = match[2] ? parseInt(match[2]) : null;
    
    let layout = layoutType;
    if (chartCount) {
      if (chartCount === 4) layout = 'grid_2x2';
      else if (chartCount === 9) layout = 'grid_3x3';
    }
    
    return {
      action: 'change_layout',
      layout,
      original: originalText
    };
  }

  // Language support methods
  setLanguage(language) {
    this.language = language;
    if (this.recognition) {
      this.recognition.lang = language;
    }
  }

  getSupportedLanguages() {
    return [
      'en-US', 'en-GB', 'en-IN',     // English variants
      'hi-IN',                        // Hindi
      'ta-IN',                        // Tamil
      'te-IN',                        // Telugu
      'bn-IN',                        // Bengali
      'gu-IN',                        // Gujarati
      'kn-IN',                        // Kannada
      'ml-IN',                        // Malayalam
      'mr-IN',                        // Marathi
      'pa-IN',                        // Punjabi
      'ur-IN'                         // Urdu
    ];
  }

  // Utility methods
  isAvailable() {
    return this.isSupported;
  }

  getStatus() {
    return {
      supported: this.isSupported,
      listening: this.isListening,
      language: this.language
    };
  }
}

export default VoiceCommands;
export { VoiceCommands };