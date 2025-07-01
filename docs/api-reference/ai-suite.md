# AI Suite APIs

## Multi-language AI Support & Market Intelligence

The GridWorks AI Suite provides comprehensive artificial intelligence services including multi-language customer support, market intelligence, content moderation, and WhatsApp Business integration. All services support 11 languages with 99% accuracy rates.

---

## 🤖 Support Engine API

### Get Support Response

Generate AI-powered responses for customer support queries in multiple languages.

**Endpoint:** `POST /api/v1/ai-suite/support/response`

**Request:**
```json
{
  "message": "How do I buy Reliance shares?",
  "language": "hi",
  "context": {
    "user_id": "user_123",
    "session_id": "session_456",
    "conversation_id": "conv_789",
    "platform": "whatsapp",
    "user_tier": "premium"
  },
  "options": {
    "include_suggestions": true,
    "include_actions": true,
    "max_response_length": 500,
    "tone": "professional"
  }
}
```

**Response:**
```json
{
  "reply": "रिलायंस के शेयर खरीदने के लिए, आपको पहले अपना ट्रेडिंग अकाउंट खोलना होगा। फिर आप 'BUY RELIANCE 100' टाइप कर सकते हैं।",
  "confidence": 0.95,
  "language": "hi",
  "detected_intent": "stock_purchase_inquiry",
  "response_time_ms": 1250,
  "suggestions": [
    "Check current Reliance stock price",
    "View your portfolio balance",
    "Set up price alerts for Reliance"
  ],
  "suggested_actions": [
    {
      "type": "place_order",
      "symbol": "RELIANCE",
      "action": "BUY",
      "description": "Place buy order for Reliance"
    }
  ],
  "context_used": {
    "conversation_history": true,
    "user_preferences": true,
    "market_context": true
  }
}
```

**Supported Languages:**
- `en` - English
- `hi` - Hindi  
- `ta` - Tamil
- `te` - Telugu
- `bn` - Bengali
- `mr` - Marathi
- `gu` - Gujarati
- `kn` - Kannada
- `ml` - Malayalam
- `pa` - Punjabi
- `ur` - Urdu

---

### Conversation History

Retrieve conversation history for context-aware responses.

**Endpoint:** `GET /api/v1/ai-suite/support/conversations/{conversation_id}`

**Response:**
```json
{
  "conversation_id": "conv_789",
  "user_id": "user_123",
  "messages": [
    {
      "timestamp": "2025-01-01T09:30:00Z",
      "type": "user",
      "message": "Hello",
      "language": "en"
    },
    {
      "timestamp": "2025-01-01T09:30:02Z", 
      "type": "assistant",
      "message": "Hello! How can I help you with your trading today?",
      "language": "en",
      "confidence": 0.98
    }
  ],
  "context": {
    "session_duration": 1800,
    "message_count": 15,
    "resolved_queries": 3,
    "satisfaction_score": 4.5
  }
}
```

---

### Bulk Response Generation

Process multiple support queries in a single request.

**Endpoint:** `POST /api/v1/ai-suite/support/bulk-response`

**Request:**
```json
{
  "queries": [
    {
      "id": "query_1",
      "message": "What is the current price of TCS?",
      "language": "en",
      "context": {"user_id": "user_123"}
    },
    {
      "id": "query_2", 
      "message": "मेरा पोर्टफोलियो कैसा चल रहा है?",
      "language": "hi",
      "context": {"user_id": "user_456"}
    }
  ],
  "options": {
    "parallel_processing": true,
    "include_confidence": true
  }
}
```

**Response:**
```json
{
  "responses": [
    {
      "query_id": "query_1",
      "reply": "The current price of TCS is ₹3,245.50, up 2.3% from yesterday's close.",
      "confidence": 0.96,
      "processing_time_ms": 1100
    },
    {
      "query_id": "query_2",
      "reply": "आपका पोर्टफोलियो आज ₹2,500 का फायदा दिखा रहा है। कुल वैल्यू ₹1,50,000 है।",
      "confidence": 0.94,
      "processing_time_ms": 1350
    }
  ],
  "total_processing_time_ms": 2450,
  "success_count": 2,
  "error_count": 0
}
```

---

## 🧠 Intelligence Engine API

### Morning Pulse

Get comprehensive pre-market analysis delivered daily at 7:30 AM IST.

**Endpoint:** `GET /api/v1/ai-suite/intelligence/morning-pulse`

**Parameters:**
- `date` (optional): Date for historical morning pulse (YYYY-MM-DD)
- `markets`: Array of markets (NSE, BSE, MCX)
- `sectors`: Array of sectors to focus on

**Response:**
```json
{
  "date": "2025-01-01",
  "generated_at": "2025-01-01T07:30:00+05:30",
  "market_outlook": "POSITIVE",
  "sentiment_score": 0.75,
  "key_highlights": [
    "Global markets ended positive with tech stocks leading gains",
    "RBI policy meeting outcomes favor market sentiment",
    "Reliance Q3 results expected to beat estimates"
  ],
  "sector_analysis": {
    "TECHNOLOGY": {
      "outlook": "BULLISH",
      "key_stocks": ["TCS", "INFY", "WIPRO"],
      "catalysts": ["Strong Q3 guidance", "Dollar strength"],
      "risks": ["Margin pressure", "Visa restrictions"]
    },
    "BANKING": {
      "outlook": "NEUTRAL",
      "key_stocks": ["HDFCBANK", "ICICIBANK", "AXISBANK"],
      "catalysts": ["Credit growth", "NIM expansion"],
      "risks": ["Asset quality concerns", "Rate cycle peak"]
    }
  },
  "global_cues": {
    "us_markets": {
      "dow_jones": "+0.8%",
      "nasdaq": "+1.2%",
      "sp500": "+0.9%"
    },
    "asian_markets": {
      "nikkei": "+0.6%",
      "hang_seng": "+1.1%",
      "shanghai": "+0.4%"
    }
  },
  "economic_events": [
    {
      "time": "09:30",
      "event": "Market Opening",
      "impact": "HIGH"
    },
    {
      "time": "11:00", 
      "event": "RBI Governor Speech",
      "impact": "MEDIUM"
    }
  ],
  "top_stock_picks": [
    {
      "symbol": "RELIANCE",
      "recommendation": "BUY",
      "target_price": 2800,
      "stop_loss": 2450,
      "rationale": "Strong refining margins and digital monetization"
    }
  ]
}
```

---

### Market Intelligence

Get AI-powered analysis for specific stocks or market segments.

**Endpoint:** `POST /api/v1/ai-suite/intelligence/market-analysis`

**Request:**
```json
{
  "symbol": "RELIANCE",
  "analysis_types": ["technical", "fundamental", "sentiment"],
  "timeframe": "1D",
  "include_price_targets": true,
  "include_risk_factors": true
}
```

**Response:**
```json
{
  "symbol": "RELIANCE",
  "current_price": 2545.30,
  "analysis_timestamp": "2025-01-01T15:30:00+05:30",
  "overall_recommendation": "BUY",
  "confidence": 0.87,
  "technical_analysis": {
    "trend": "BULLISH",
    "support_levels": [2500, 2450, 2400],
    "resistance_levels": [2600, 2650, 2700],
    "indicators": {
      "rsi": 65.4,
      "macd": "BULLISH_CROSSOVER",
      "moving_averages": {
        "20_day": 2510.50,
        "50_day": 2485.25,
        "200_day": 2420.80
      }
    },
    "chart_patterns": ["ASCENDING_TRIANGLE", "HIGHER_HIGHS"]
  },
  "fundamental_analysis": {
    "pe_ratio": 23.5,
    "pb_ratio": 1.8,
    "debt_to_equity": 0.35,
    "roe": 12.8,
    "revenue_growth": "8.5%",
    "profit_growth": "12.3%",
    "sector_comparison": "OUTPERFORMING"
  },
  "sentiment_analysis": {
    "overall_sentiment": "POSITIVE",
    "sentiment_score": 0.78,
    "news_sentiment": 0.82,
    "social_sentiment": 0.74,
    "analyst_sentiment": 0.85,
    "key_sentiment_drivers": [
      "Strong Q3 results expectations",
      "Jio IPO buzz",
      "Refining margin improvement"
    ]
  },
  "price_targets": [
    {
      "analyst": "AI_CONSENSUS",
      "target": 2750,
      "timeframe": "3_MONTHS",
      "probability": 0.75
    },
    {
      "analyst": "TECHNICAL_MODEL",
      "target": 2800,
      "timeframe": "6_MONTHS", 
      "probability": 0.68
    }
  ],
  "risk_factors": [
    {
      "factor": "Oil price volatility",
      "impact": "MEDIUM",
      "probability": 0.4
    },
    {
      "factor": "Regulatory changes in telecom",
      "impact": "LOW",
      "probability": 0.2
    }
  ]
}
```

---

### Correlation Analysis

Analyze correlations between stocks, sectors, and market factors.

**Endpoint:** `POST /api/v1/ai-suite/intelligence/correlation`

**Request:**
```json
{
  "primary_symbol": "RELIANCE",
  "correlation_with": ["NIFTY50", "CRUDE_OIL", "USD_INR"],
  "timeframe": "6M",
  "correlation_type": "pearson"
}
```

**Response:**
```json
{
  "primary_symbol": "RELIANCE",
  "analysis_period": "6M",
  "correlations": [
    {
      "symbol": "NIFTY50",
      "correlation": 0.78,
      "strength": "STRONG_POSITIVE",
      "significance": 0.95
    },
    {
      "symbol": "CRUDE_OIL",
      "correlation": 0.45,
      "strength": "MODERATE_POSITIVE",
      "significance": 0.88
    },
    {
      "symbol": "USD_INR",
      "correlation": -0.32,
      "strength": "WEAK_NEGATIVE",
      "significance": 0.72
    }
  ],
  "sector_correlations": {
    "ENERGY": 0.89,
    "PETROCHEMICALS": 0.92,
    "TELECOMMUNICATIONS": 0.34
  },
  "insights": [
    "Strong positive correlation with oil prices indicates sensitivity to energy sector movements",
    "High correlation with Nifty suggests systematic risk exposure",
    "Weak negative correlation with USD/INR shows some currency hedge characteristics"
  ]
}
```

---

## 🛡️ Moderation Engine API

### Content Moderation

Analyze and moderate content for compliance, spam, and inappropriate material.

**Endpoint:** `POST /api/v1/ai-suite/moderation/analyze`

**Request:**
```json
{
  "content": "🚀🚀 AMAZING stock tip! Guaranteed 500% returns in 30 days! WhatsApp me for details! 📈💰",
  "content_type": "message",
  "context": {
    "platform": "whatsapp",
    "user_id": "user_123",
    "user_tier": "basic",
    "previous_violations": 2
  },
  "moderation_rules": ["spam", "misleading_claims", "financial_advice", "emoji_spam"]
}
```

**Response:**
```json
{
  "moderation_id": "mod_12345",
  "approved": false,
  "confidence": 0.96,
  "overall_risk_score": 0.89,
  "flags": [
    {
      "type": "MISLEADING_FINANCIAL_CLAIMS",
      "severity": "HIGH",
      "confidence": 0.94,
      "details": "Content contains unrealistic return guarantees",
      "violated_rule": "No guaranteed return promises"
    },
    {
      "type": "EXCESSIVE_EMOJIS",
      "severity": "MEDIUM",
      "confidence": 0.87,
      "details": "Emoji density above threshold (15%)",
      "violated_rule": "Emoji usage limit"
    },
    {
      "type": "SPAM_PATTERNS",
      "severity": "HIGH",
      "confidence": 0.91,
      "details": "Multiple spam indicators detected",
      "violated_rule": "Anti-spam policy"
    }
  ],
  "recommendations": [
    "Block content from posting",
    "Flag user for manual review",
    "Send educational content about investment risks"
  ],
  "suggested_actions": [
    {
      "action": "BLOCK_CONTENT",
      "auto_execute": true
    },
    {
      "action": "USER_WARNING",
      "auto_execute": false,
      "requires_review": true
    }
  ],
  "alternative_content": "Consider sharing educational content about market analysis and risk management instead.",
  "compliance_notes": "Content violates SEBI guidelines on misleading investment advice"
}
```

---

### Expert Verification

Verify credentials and authenticity of financial experts and advisors.

**Endpoint:** `POST /api/v1/ai-suite/moderation/expert-verification`

**Request:**
```json
{
  "expert_id": "expert_123",
  "credentials": {
    "certifications": ["CFP", "CFA", "FRM"],
    "experience_years": 8,
    "specialization": ["equity_analysis", "portfolio_management"],
    "education": "MBA Finance from IIM Ahmedabad",
    "license_numbers": ["SEBI_REG_12345", "AMFI_ARN_67890"]
  },
  "verification_documents": [
    "https://storage.gridworks.com/docs/certificate_cfa.pdf",
    "https://storage.gridworks.com/docs/sebi_license.pdf"
  ],
  "social_proof": {
    "linkedin_profile": "https://linkedin.com/in/expert123",
    "published_research": ["https://research.com/paper1", "https://research.com/paper2"],
    "media_appearances": 15
  }
}
```

**Response:**
```json
{
  "verification_id": "verify_456",
  "expert_id": "expert_123",
  "verification_status": "VERIFIED",
  "verification_level": "LEVEL_3_EXPERT",
  "confidence_score": 0.94,
  "verification_details": {
    "credentials_verified": true,
    "documents_authentic": true,
    "regulatory_compliance": true,
    "background_check_passed": true,
    "social_proof_validated": true
  },
  "verified_credentials": [
    {
      "certification": "CFA",
      "issuer": "CFA Institute",
      "verified": true,
      "expiry_date": "2027-12-31"
    },
    {
      "license": "SEBI_REG_12345",
      "issuer": "SEBI",
      "verified": true,
      "status": "ACTIVE"
    }
  ],
  "expert_rating": {
    "overall_score": 4.7,
    "expertise_depth": 4.8,
    "track_record": 4.6,
    "communication_quality": 4.7,
    "compliance_history": 5.0
  },
  "allowed_activities": [
    "PROVIDE_INVESTMENT_ADVICE",
    "CONDUCT_WEBINARS",
    "PUBLISH_RESEARCH",
    "MANAGE_PORTFOLIOS"
  ],
  "restrictions": [],
  "verification_valid_until": "2025-12-31T23:59:59Z"
}
```

---

## 📱 WhatsApp Business API

### Send Message

Send WhatsApp Business messages with template support.

**Endpoint:** `POST /api/v1/ai-suite/whatsapp/send`

**Request:**
```json
{
  "to": "+919876543210",
  "message_type": "template",
  "template": {
    "name": "order_confirmation",
    "language": "hi",
    "parameters": [
      "RELIANCE",
      "100",
      "₹2,545.30",
      "₹2,54,530"
    ]
  },
  "fallback_message": {
    "type": "text",
    "content": "आपका ऑर्डर सफलतापूर्वक प्लेस हो गया है।"
  }
}
```

**Response:**
```json
{
  "message_id": "wamid.12345",
  "status": "SENT",
  "timestamp": "2025-01-01T15:30:00+05:30",
  "to": "+919876543210",
  "billing_info": {
    "conversation_category": "SERVICE",
    "billable": true,
    "cost": 0.005
  }
}
```

---

### Message Templates

Manage WhatsApp Business message templates.

**Endpoint:** `GET /api/v1/ai-suite/whatsapp/templates`

**Response:**
```json
{
  "templates": [
    {
      "name": "order_confirmation",
      "status": "APPROVED",
      "language": "hi",
      "category": "TRANSACTIONAL",
      "template": "आपका {{1}} का ऑर्डर {{2}} शेयर्स के लिए ₹{{3}} प्रति शेयर पर प्लेस हो गया है। कुल राशि: {{4}}",
      "parameters": ["stock_name", "quantity", "price", "total_amount"]
    },
    {
      "name": "price_alert",
      "status": "APPROVED", 
      "language": "en",
      "category": "UTILITY",
      "template": "🔔 Price Alert: {{1}} has reached ₹{{2}}, {{3}} from your target price of ₹{{4}}",
      "parameters": ["stock_name", "current_price", "direction", "target_price"]
    }
  ]
}
```

---

### Webhook Processing

Process incoming WhatsApp webhooks for automated responses.

**Endpoint:** `POST /api/v1/ai-suite/whatsapp/webhook`

**Request (Webhook payload):**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "ENTRY_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "919876543210",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "messages": [
              {
                "from": "919876543211",
                "id": "wamid.MESSAGE_ID",
                "timestamp": "1672531200",
                "text": {
                  "body": "Check RELIANCE price"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "processed": true,
  "response_sent": true,
  "processing_time_ms": 850,
  "actions_taken": [
    {
      "action": "STOCK_PRICE_QUERY",
      "symbol": "RELIANCE",
      "response_sent": true,
      "message_id": "wamid.RESPONSE_12345"
    }
  ],
  "user_context_updated": true
}
```

---

## 🔊 Voice Features API

### Text-to-Speech

Convert text responses to speech for voice-enabled interactions.

**Endpoint:** `POST /api/v1/ai-suite/voice/text-to-speech`

**Request:**
```json
{
  "text": "रिलायंस का आज का भाव ₹2,545.30 है, कल के मुकाबले 2.3% ऊपर है।",
  "language": "hi",
  "voice_settings": {
    "gender": "female",
    "speed": 1.0,
    "pitch": 0.0,
    "voice_id": "hi-IN-FEMALE-1"
  },
  "output_format": "mp3"
}
```

**Response:**
```json
{
  "audio_url": "https://storage.gridworks.com/audio/tts_12345.mp3",
  "duration_seconds": 8.5,
  "file_size_bytes": 136000,
  "voice_used": "hi-IN-FEMALE-1",
  "processing_time_ms": 2100
}
```

---

### Speech-to-Text

Convert voice messages to text for processing.

**Endpoint:** `POST /api/v1/ai-suite/voice/speech-to-text`

**Request:**
```json
{
  "audio_url": "https://storage.gridworks.com/audio/voice_message.ogg",
  "language": "hi",
  "audio_format": "ogg",
  "enhance_audio": true
}
```

**Response:**
```json
{
  "transcription": "रिलायंस का प्राइस क्या है आज का",
  "confidence": 0.92,
  "language_detected": "hi",
  "processing_time_ms": 3200,
  "audio_quality": "GOOD",
  "speaker_info": {
    "gender": "MALE",
    "estimated_age": "25-35",
    "accent": "NORTH_INDIAN"
  }
}
```

---

## 📊 Analytics API

### AI Performance Metrics

Get analytics on AI service performance and usage.

**Endpoint:** `GET /api/v1/ai-suite/analytics/performance`

**Parameters:**
- `start_date`: Start date for metrics (YYYY-MM-DD)
- `end_date`: End date for metrics (YYYY-MM-DD)
- `service`: Specific service (support, intelligence, moderation)
- `language`: Filter by language

**Response:**
```json
{
  "period": {
    "start_date": "2024-12-01",
    "end_date": "2024-12-31"
  },
  "overall_metrics": {
    "total_requests": 125000,
    "average_response_time_ms": 1250,
    "success_rate": 0.995,
    "average_confidence": 0.89
  },
  "service_breakdown": {
    "support": {
      "requests": 75000,
      "avg_response_time_ms": 1100,
      "success_rate": 0.997,
      "avg_confidence": 0.91,
      "languages": {
        "hi": 35000,
        "en": 25000,
        "ta": 8000,
        "other": 7000
      }
    },
    "intelligence": {
      "requests": 30000,
      "avg_response_time_ms": 1800,
      "success_rate": 0.992,
      "avg_confidence": 0.87
    },
    "moderation": {
      "requests": 20000,
      "avg_response_time_ms": 800,
      "success_rate": 0.998,
      "blocked_content": 1250
    }
  },
  "quality_metrics": {
    "user_satisfaction": 4.6,
    "resolution_rate": 0.94,
    "escalation_rate": 0.06,
    "feedback_score": 4.5
  }
}
```

---

## 🚨 Error Codes

### Common Error Responses

```json
{
  "error": {
    "code": "INVALID_LANGUAGE",
    "message": "Unsupported language code provided",
    "details": "Language 'xyz' is not supported. Supported languages: en, hi, ta, te, bn, mr, gu, kn, ml, pa, ur"
  }
}
```

### Error Code Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `INVALID_LANGUAGE` | Unsupported language code | Use supported language codes |
| `CONFIDENCE_TOO_LOW` | AI confidence below threshold | Retry with more context |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `CONTENT_BLOCKED` | Content flagged by moderation | Review and modify content |
| `EXPERT_NOT_VERIFIED` | Expert verification failed | Complete verification process |
| `WHATSAPP_TEMPLATE_NOT_FOUND` | Template doesn't exist | Create or use existing template |
| `VOICE_SYNTHESIS_FAILED` | TTS generation failed | Retry with shorter text |
| `AUDIO_FORMAT_UNSUPPORTED` | Audio format not supported | Convert to supported format |

---

## 🔒 Authentication

All AI Suite APIs require authentication via API key:

```bash
curl -X POST https://api.gridworks.com/api/v1/ai-suite/support/response \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "en"}'
```

## 📈 Rate Limits

| Service | Requests per Minute | Burst Limit |
|---------|-------------------|-------------|
| Support Engine | 1000 | 1500 |
| Intelligence Engine | 500 | 750 |
| Moderation Engine | 2000 | 3000 |
| WhatsApp API | 100 | 150 |
| Voice API | 200 | 300 |

## 🌍 Available Regions

- **India**: Primary region with full language support
- **US**: English-only support
- **EU**: English and select European languages
- **APAC**: English and local language support

---

The GridWorks AI Suite APIs provide comprehensive artificial intelligence capabilities with enterprise-grade reliability, multi-language support, and advanced features for financial services applications.