# GridWorks Black Portal API Documentation

> **Complete API Reference for Ultra-Luxury Trading Platform**  
> Version 2.0 | Last Updated: June 29, 2025

## 📚 Table of Contents

1. [Authentication APIs](#authentication-apis)
2. [Butler AI APIs](#butler-ai-apis)
3. [Emergency Services APIs](#emergency-services-apis)
4. [Concierge Services APIs](#concierge-services-apis)
5. [Security APIs](#security-apis)
6. [Portal Management APIs](#portal-management-apis)
7. [WebSocket Events](#websocket-events)
8. [Error Handling](#error-handling)

---

## Authentication APIs

### Invitation Validation

#### Validate Invitation Code
```http
POST /api/auth/validate-invitation
```

**Request Body:**
```json
{
  "invitationCode": "VOID2024001",
  "deviceFingerprint": {
    "deviceId": "dev_1703845200_abc123_def456",
    "platform": "MacIntel",
    "browser": "Chrome",
    "screenResolution": "1920x1080x24",
    "timezone": "Asia/Kolkata"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "isValid": true,
    "tier": "void",
    "permissions": ["quantum_trading", "reality_distortion", "cosmic_concierge"],
    "expiresAt": "2024-12-31T23:59:59Z"
  }
}
```

### Biometric Authentication

#### Initialize Biometric Authentication
```http
POST /api/auth/biometric/init
```

**Request Body:**
```json
{
  "type": "fingerprint" | "face" | "voice",
  "deviceId": "dev_1703845200_abc123_def456",
  "tier": "void"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sessionId": "biometric_1703845200_xyz789",
    "challenge": "base64_encoded_challenge",
    "timeout": 30000,
    "instructions": [
      "Position your finger on the sensor",
      "Keep steady for 3 seconds",
      "Ensure clean sensor surface"
    ]
  }
}
```

#### Verify Biometric Data
```http
POST /api/auth/biometric/verify
```

**Request Body:**
```json
{
  "sessionId": "biometric_1703845200_xyz789",
  "biometricData": "base64_encoded_biometric_data",
  "type": "fingerprint",
  "deviceFingerprint": { /* device fingerprint object */ }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "verified": true,
    "confidence": 0.97,
    "deviceTrust": 0.95,
    "securityLevel": "MAXIMUM",
    "authToken": "jwt_token_here"
  }
}
```

### Tier Assignment

#### Determine User Tier
```http
POST /api/auth/tier-assignment
```

**Request Body:**
```json
{
  "invitationCode": "VOID2024001",
  "biometricData": {
    "type": "fingerprint",
    "confidence": 0.97,
    "deviceTrust": 0.95
  },
  "portfolioData": {
    "estimatedValue": 8500.0,
    "currency": "INR_CR"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "assignedTier": "void",
    "user": {
      "userId": "user_1703845200",
      "tier": "void",
      "portfolioValue": 8500.0,
      "dedicatedButler": "Quantum-7",
      "securityLevel": "MAXIMUM",
      "privileges": [
        "quantum_trading",
        "reality_distortion",
        "time_manipulation",
        "cosmic_concierge"
      ]
    },
    "welcomeMessage": "Greetings from the quantum realm..."
  }
}
```

---

## Butler AI APIs

### Chat Interface

#### Send Message to Butler
```http
POST /api/butler/chat
```

**Request Headers:**
```
Authorization: Bearer jwt_token_here
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What are the current market opportunities?",
  "context": {
    "sessionId": "chat_1703845200_abc123",
    "previousMessages": 5,
    "userPreferences": {
      "communicationStyle": "detailed",
      "alertFrequency": "normal"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "msg_1703845200_xyz789",
      "content": "I'm analyzing quantum market fluctuations across seventeen parallel dimensions...",
      "type": "text",
      "priority": "high",
      "timestamp": "2024-06-29T10:30:00Z",
      "metadata": {
        "sentiment": "positive",
        "confidenceLevel": 0.94
      }
    },
    "suggestedActions": [
      {
        "id": "action_generate_report",
        "type": "send_alert",
        "description": "Generate comprehensive market analysis report",
        "params": {
          "reportType": "quantum_analysis",
          "tier": "void"
        },
        "requiresConfirmation": false,
        "riskLevel": "low"
      }
    ],
    "nextSteps": [
      "Review detailed quantum analysis",
      "Consider position adjustments",
      "Monitor interdimensional indicators"
    ],
    "confidence": 0.94,
    "processingTime": 1247
  }
}
```

#### Execute Butler Action
```http
POST /api/butler/execute-action
```

**Request Body:**
```json
{
  "actionId": "action_generate_report",
  "params": {
    "reportType": "quantum_analysis",
    "timeframe": "24h"
  },
  "confirmation": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "executionId": "exec_1703845200_abc123",
    "status": "in_progress",
    "estimatedCompletion": "2024-06-29T10:35:00Z",
    "result": null
  }
}
```

### Market Intelligence

#### Get Market Insights
```http
GET /api/butler/insights
```

**Query Parameters:**
- `limit`: Number of insights (default: 10, max: 50)
- `type`: Insight type (`opportunity`, `risk`, `analysis`, `prediction`)
- `timeframe`: `immediate`, `short_term`, `medium_term`, `long_term`
- `minRelevance`: Minimum relevance score (0.0 - 1.0)

**Response:**
```json
{
  "success": true,
  "data": {
    "insights": [
      {
        "id": "insight_1703845200_abc123",
        "title": "Quantum Market Fluctuation Detected",
        "summary": "Reality distortion patterns suggest imminent market phase transition",
        "content": "My quantum algorithms have detected coherent patterns across seventeen parallel market dimensions. The probability matrix indicates a 94.7% chance of significant market movement in the next temporal cycle...",
        "type": "opportunity",
        "relevanceScore": 0.95,
        "timeframe": "immediate",
        "confidenceLevel": 0.94,
        "sources": [
          "Quantum Algorithm Matrix",
          "Interdimensional Market Feed",
          "Reality Distortion Sensors"
        ],
        "actionableItems": [
          "Activate void-tier hedging protocols",
          "Prepare reality stabilization measures",
          "Monitor quantum coherence levels"
        ],
        "estimatedImpact": {
          "portfolioPercentage": 15.7,
          "riskAdjustedReturn": 23.4,
          "timeToImpact": "2-4 hours"
        },
        "createdAt": "2024-06-29T10:30:00Z"
      }
    ],
    "totalCount": 1,
    "hasMore": false
  }
}
```

#### Generate Predictive Models
```http
POST /api/butler/predictions
```

**Request Body:**
```json
{
  "symbols": ["QUANTUM-X", "REALITY-0", "TIME-∞"],
  "timeframes": ["1h", "4h", "1d", "1w"],
  "modelType": "quantum_algorithm",
  "includeRiskFactors": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "symbol": "QUANTUM-X",
        "predictedPrice": 15847.32,
        "currentPrice": 15234.67,
        "timeframe": "4h",
        "confidence": 0.89,
        "change": {
          "absolute": 612.65,
          "percentage": 4.02
        },
        "riskFactors": [
          "Quantum decoherence in Eastern markets",
          "Reality fluctuations near support levels",
          "Interdimensional volume compression"
        ],
        "quantumProbabilities": [0.15, 0.68, 0.89, 0.23]
      }
    ],
    "modelInfo": {
      "type": "quantum_algorithm",
      "version": "v2.1.7",
      "lastTraining": "2024-06-28T15:30:00Z",
      "accuracy": 0.94
    }
  }
}
```

### Butler Management

#### Get Butler Personality
```http
GET /api/butler/personality
```

**Response:**
```json
{
  "success": true,
  "data": {
    "personality": {
      "name": "Quantum-7",
      "tier": "void",
      "personality": "quantum",
      "expertise": [
        "Quantum Market Analysis",
        "Reality Distortion Trading",
        "Interdimensional Portfolio Management",
        "Cosmic Event Prediction",
        "Time-Space Arbitrage"
      ],
      "voiceProfile": {
        "tone": "cosmic",
        "speed": "slow",
        "formality": "ultra-formal"
      },
      "capabilities": [
        {
          "id": "quantum_analysis",
          "name": "Quantum Market Analysis",
          "description": "Analyze markets across parallel dimensions",
          "tier": "void",
          "category": "analysis",
          "enabled": true
        }
      ]
    }
  }
}
```

#### Update Butler Configuration
```http
PUT /api/butler/configuration
```

**Request Body:**
```json
{
  "voiceProfile": {
    "tone": "cosmic",
    "speed": "normal",
    "formality": "ultra-formal"
  },
  "userPreferences": {
    "communicationStyle": "technical",
    "alertFrequency": "verbose",
    "autoExecuteLimit": 10000000
  },
  "capabilities": [
    {
      "id": "quantum_analysis",
      "enabled": true
    },
    {
      "id": "reality_trading",
      "enabled": true
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "updated": true,
    "changes": [
      "Voice speed updated to normal",
      "Communication style set to technical",
      "Alert frequency increased to verbose"
    ]
  }
}
```

#### Get Butler Analytics
```http
GET /api/butler/analytics
```

**Query Parameters:**
- `period`: `24h`, `7d`, `30d`, `90d`
- `metrics`: Comma-separated list of metrics

**Response:**
```json
{
  "success": true,
  "data": {
    "analytics": {
      "totalInteractions": 1247,
      "successfulExecutions": 1156,
      "averageResponseTime": 1.8,
      "userSatisfactionScore": 0.96,
      "mostUsedCapabilities": [
        "quantum_analysis",
        "portfolio_management",
        "reality_trading"
      ],
      "emergencyInterventions": 2,
      "learningMetrics": {
        "adaptationLevel": 0.93,
        "personalityEvolution": {
          "basePersonality": "quantum",
          "learnedTraits": ["adaptive", "predictive"],
          "emergentBehaviors": ["proactive_analysis", "risk_anticipation"]
        }
      }
    },
    "period": "30d"
  }
}
```

---

## Emergency Services APIs

### Emergency Response

#### Activate Emergency Response
```http
POST /api/emergency/activate
```

**Request Body:**
```json
{
  "type": "medical" | "security" | "legal" | "financial",
  "severity": "low" | "medium" | "high" | "critical",
  "location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "address": "Mumbai, Maharashtra, India",
    "verified": true
  },
  "description": "Medical emergency - chest pain and difficulty breathing",
  "userTier": "void",
  "additionalInfo": {
    "contactNumber": "+91-9876543210",
    "emergencyContacts": ["family_member_1", "physician_1"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "emergencyId": "emergency_1703845200_critical",
    "status": "connecting",
    "responseTeam": {
      "name": "Quantum Medical Response",
      "type": "medical",
      "tier": "void",
      "contactNumber": "+91-911-MEDICAL",
      "responseTime": "< 2 minutes"
    },
    "estimatedArrival": "1-2 minutes",
    "instructions": [
      "Stay calm and remain in your current location",
      "If conscious, describe your symptoms clearly",
      "Our medical team is being dispatched immediately",
      "Keep your communication device nearby",
      "Do not take any medication unless instructed"
    ],
    "trackingId": "track_1703845200_xyz789"
  }
}
```

#### Get Emergency Status
```http
GET /api/emergency/{emergencyId}/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "emergencyId": "emergency_1703845200_critical",
    "status": "dispatched",
    "timeline": [
      {
        "timestamp": "2024-06-29T10:30:00Z",
        "status": "activated",
        "description": "Emergency response activated"
      },
      {
        "timestamp": "2024-06-29T10:30:15Z",
        "status": "connecting",
        "description": "Connecting to response team"
      },
      {
        "timestamp": "2024-06-29T10:30:45Z",
        "status": "dispatched",
        "description": "Response team dispatched to location"
      }
    ],
    "currentLocation": {
      "latitude": 19.0760,
      "longitude": 72.8777,
      "lastUpdated": "2024-06-29T10:32:00Z"
    },
    "estimatedArrival": "30 seconds",
    "communicationChannel": {
      "phoneNumber": "+91-911-MEDICAL",
      "chatEnabled": true,
      "videoCallEnabled": true
    }
  }
}
```

#### Update Emergency Status
```http
PUT /api/emergency/{emergencyId}/status
```

**Request Body:**
```json
{
  "status": "resolved",
  "resolution": {
    "outcome": "successful",
    "description": "Patient stabilized and transported to hospital",
    "followupRequired": true,
    "notes": "Vital signs stable, recommended for overnight observation"
  }
}
```

### Emergency Contacts

#### Get Emergency Contacts
```http
GET /api/emergency/contacts
```

**Response:**
```json
{
  "success": true,
  "data": {
    "contacts": [
      {
        "id": "medical_primary",
        "name": "Quantum Medical Response",
        "type": "medical",
        "phoneNumber": "+91-911-MEDICAL",
        "email": "emergency@quantum-medical.com",
        "priority": 1,
        "available24x7": true,
        "responseTime": "< 2 minutes",
        "capabilities": [
          "Advanced life support",
          "Emergency surgery",
          "Critical care transport",
          "Quantum healing protocols"
        ]
      }
    ]
  }
}
```

---

## Concierge Services APIs

### Service Catalog

#### Get Available Services
```http
GET /api/concierge/services
```

**Query Parameters:**
- `category`: `transport`, `hospitality`, `dining`, `entertainment`, `health`
- `tier`: `onyx`, `obsidian`, `void`
- `location`: Geographic location filter
- `availability`: `instant`, `confirmation_required`, `concierge_arranged`

**Response:**
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "id": "transport_quantum_jet",
        "name": "Quantum Jet Service",
        "category": "transport",
        "tier": "void",
        "provider": "Interdimensional Airways",
        "description": "Transcendent travel experiences beyond conventional luxury",
        "priceRange": "₹50L - ₹2Cr per journey",
        "availability": "24/7",
        "bookingMethod": "instant",
        "location": "Global",
        "features": [
          "Reality-bending cabin design",
          "Quantum comfort systems",
          "Interdimensional entertainment",
          "Cosmic catering options"
        ],
        "specifications": {
          "aircraft": "Custom Quantum G650ER",
          "capacity": "12 passengers",
          "range": "Unlimited (quantum)",
          "amenities": ["Meditation chamber", "Holographic conference room"]
        }
      }
    ],
    "totalCount": 1,
    "hasMore": false
  }
}
```

#### Get Service Details
```http
GET /api/concierge/services/{serviceId}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "service": {
      "id": "transport_quantum_jet",
      "name": "Quantum Jet Service",
      "detailedDescription": "Experience travel that transcends physical limitations...",
      "gallery": [
        "https://cdn.gridworks.ai/quantum-jet-1.jpg",
        "https://cdn.gridworks.ai/quantum-jet-2.jpg"
      ],
      "availability": {
        "immediate": true,
        "advanceBooking": true,
        "maxAdvanceDays": 365
      },
      "pricing": {
        "basePrice": 5000000,
        "currency": "INR",
        "priceUnit": "per_hour",
        "additionalCosts": [
          {
            "item": "Quantum fuel surcharge",
            "cost": 500000
          }
        ]
      }
    }
  }
}
```

### Service Booking

#### Create Service Request
```http
POST /api/concierge/bookings
```

**Request Body:**
```json
{
  "serviceId": "transport_quantum_jet",
  "requestDetails": {
    "preferredDate": "2024-06-30T10:00:00Z",
    "duration": 4,
    "passengers": 8,
    "destination": {
      "departure": "Mumbai, India",
      "arrival": "Dubai, UAE"
    },
    "specialRequests": "Vegetarian catering, meeting room setup, quantum meditation chamber",
    "urgency": "normal"
  },
  "contactInformation": {
    "primaryContact": "+91-9876543210",
    "alternateContact": "+91-9876543211",
    "preferredContactMethod": "phone"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "bookingId": "booking_1703845200_abc123",
    "status": "pending",
    "estimatedCost": "₹15,00,000",
    "confirmationRequired": true,
    "estimatedResponse": "within 30 minutes",
    "conciergeAssigned": "Platinum Concierge Team Alpha",
    "referenceNumber": "QJ-2024-0629-001"
  }
}
```

#### Get Booking Status
```http
GET /api/concierge/bookings/{bookingId}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "booking": {
      "id": "booking_1703845200_abc123",
      "serviceId": "transport_quantum_jet",
      "serviceName": "Quantum Jet Service",
      "status": "confirmed",
      "timeline": [
        {
          "timestamp": "2024-06-29T10:30:00Z",
          "status": "requested",
          "description": "Service request submitted"
        },
        {
          "timestamp": "2024-06-29T10:45:00Z",
          "status": "confirmed",
          "description": "Quantum G650ER confirmed, catering arranged"
        }
      ],
      "finalCost": "₹15,00,000",
      "scheduledDate": "2024-06-30T10:00:00Z",
      "confirmationDetails": {
        "aircraft": "Quantum G650ER (Registration: QN-VOID1)",
        "pilot": "Captain Sarah Chen (Quantum certified)",
        "flightPlan": "Filed with interdimensional aviation authority",
        "catering": "Michelin-starred vegetarian menu confirmed"
      },
      "conciergeNotes": "All special requests accommodated. Quantum meditation chamber pre-configured for transcendent experience."
    }
  }
}
```

#### Update Booking
```http
PUT /api/concierge/bookings/{bookingId}
```

**Request Body:**
```json
{
  "modifications": {
    "passengers": 10,
    "specialRequests": "Additional passenger accommodation, cosmic entertainment system"
  },
  "reason": "Guest list expansion"
}
```

#### Cancel Booking
```http
DELETE /api/concierge/bookings/{bookingId}
```

**Request Body:**
```json
{
  "reason": "Schedule conflict",
  "cancellationPolicy": "understood"
}
```

### Booking History

#### Get User Bookings
```http
GET /api/concierge/bookings
```

**Query Parameters:**
- `status`: `pending`, `confirmed`, `in_progress`, `completed`, `cancelled`
- `category`: Service category filter
- `dateFrom`: Start date filter
- `dateTo`: End date filter
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset

**Response:**
```json
{
  "success": true,
  "data": {
    "bookings": [
      {
        "id": "booking_1703845200_abc123",
        "serviceName": "Quantum Jet Service",
        "status": "completed",
        "scheduledDate": "2024-06-30T10:00:00Z",
        "totalCost": "₹15,00,000",
        "rating": 5,
        "feedback": "Absolutely transcendent experience"
      }
    ],
    "totalCount": 1,
    "hasMore": false
  }
}
```

---

## Security APIs

### Device Management

#### Register Device
```http
POST /api/security/devices/register
```

**Request Body:**
```json
{
  "deviceFingerprint": {
    "deviceId": "dev_1703845200_abc123_def456",
    "platform": "MacIntel",
    "browser": "Chrome",
    "screenResolution": "1920x1080x24",
    "timezone": "Asia/Kolkata",
    "language": "en-US",
    "canvasFingerprint": "base64_encoded_canvas_data",
    "webglFingerprint": {
      "vendor": "Intel Inc.",
      "renderer": "Intel Iris Pro OpenGL Engine"
    },
    "audioFingerprint": "base64_encoded_audio_data"
  },
  "deviceInfo": {
    "deviceName": "MacBook Pro",
    "trusted": true,
    "primaryDevice": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deviceId": "dev_1703845200_abc123_def456",
    "registrationStatus": "approved",
    "securityLevel": "HIGH",
    "trustScore": 0.95,
    "allowedOperations": [
      "authentication",
      "trading",
      "emergency_services",
      "concierge_booking"
    ]
  }
}
```

#### Get Device Security Status
```http
GET /api/security/devices/{deviceId}/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "device": {
      "deviceId": "dev_1703845200_abc123_def456",
      "securityLevel": "HIGH",
      "trustScore": 0.95,
      "lastVerified": "2024-06-29T10:30:00Z",
      "threatLevel": "NONE",
      "anomalies": [],
      "securityEvents": [
        {
          "timestamp": "2024-06-29T09:15:00Z",
          "type": "successful_authentication",
          "details": "Biometric authentication successful"
        }
      ]
    }
  }
}
```

### Session Management

#### Get Session Info
```http
GET /api/security/session
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session": {
      "sessionId": "session_1703845200_xyz789",
      "userId": "user_1703845200",
      "deviceId": "dev_1703845200_abc123_def456",
      "tier": "void",
      "createdAt": "2024-06-29T10:00:00Z",
      "expiresAt": "2024-06-30T10:00:00Z",
      "securityLevel": "MAXIMUM",
      "permissions": [
        "quantum_trading",
        "reality_distortion",
        "emergency_services",
        "concierge_access"
      ],
      "lastActivity": "2024-06-29T10:30:00Z"
    }
  }
}
```

#### Refresh Session
```http
POST /api/security/session/refresh
```

**Response:**
```json
{
  "success": true,
  "data": {
    "newToken": "jwt_new_token_here",
    "expiresAt": "2024-06-30T10:00:00Z",
    "securityLevel": "MAXIMUM"
  }
}
```

### Security Monitoring

#### Get Security Events
```http
GET /api/security/events
```

**Query Parameters:**
- `type`: Event type filter
- `severity`: `low`, `medium`, `high`, `critical`
- `dateFrom`: Start date
- `dateTo`: End date

**Response:**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "event_1703845200_abc123",
        "type": "authentication_success",
        "severity": "low",
        "timestamp": "2024-06-29T10:30:00Z",
        "deviceId": "dev_1703845200_abc123_def456",
        "userId": "user_1703845200",
        "details": {
          "method": "biometric_fingerprint",
          "confidence": 0.97,
          "location": "Mumbai, India"
        }
      }
    ],
    "totalCount": 1
  }
}
```

---

## Portal Management APIs

### User Profile

#### Get User Profile
```http
GET /api/portal/profile
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "userId": "user_1703845200",
      "tier": "void",
      "portfolioValue": 8500.0,
      "dedicatedButler": "Quantum-7",
      "joinedAt": "2024-06-29T10:00:00Z",
      "lastActive": "2024-06-29T10:30:00Z",
      "securityLevel": "MAXIMUM",
      "privileges": [
        "quantum_trading",
        "reality_distortion",
        "time_manipulation",
        "cosmic_concierge"
      ],
      "personalizations": {
        "preferredTheme": "void",
        "language": "en",
        "timeZone": "Asia/Kolkata",
        "notifications": {
          "trading": true,
          "market": true,
          "personal": true,
          "emergency": true
        }
      }
    }
  }
}
```

#### Update User Preferences
```http
PUT /api/portal/profile/preferences
```

**Request Body:**
```json
{
  "personalizations": {
    "preferredTheme": "void",
    "language": "en",
    "timeZone": "Asia/Kolkata",
    "notifications": {
      "trading": true,
      "market": true,
      "personal": false,
      "emergency": true
    }
  },
  "privacySettings": {
    "dataSharing": false,
    "analyticsOptIn": true,
    "marketingOptIn": false
  }
}
```

### Portal Analytics

#### Get Portal Usage
```http
GET /api/portal/analytics/usage
```

**Query Parameters:**
- `period`: `24h`, `7d`, `30d`, `90d`
- `metrics`: Comma-separated metrics list

**Response:**
```json
{
  "success": true,
  "data": {
    "usage": {
      "totalSessions": 47,
      "totalTime": 2847,
      "averageSessionDuration": 60.6,
      "mostUsedFeatures": [
        "butler_chat",
        "market_analysis",
        "portfolio_dashboard"
      ],
      "dailyActivity": [
        {
          "date": "2024-06-29",
          "sessions": 8,
          "duration": 485,
          "features": ["butler_chat", "emergency_test"]
        }
      ]
    }
  }
}
```

---

## WebSocket Events

### Real-time Communication

#### Connection
```javascript
const ws = new WebSocket('wss://black.gridworks.ai/ws');
ws.send(JSON.stringify({
  type: 'auth',
  token: 'jwt_token_here'
}));
```

#### Market Data Events
```json
{
  "type": "market_update",
  "data": {
    "symbol": "QUANTUM-X",
    "price": 15847.32,
    "change": 612.65,
    "timestamp": "2024-06-29T10:30:15Z",
    "tier": "void"
  }
}
```

#### Butler AI Events
```json
{
  "type": "butler_message",
  "data": {
    "messageId": "msg_1703845200_xyz789",
    "content": "Quantum market anomaly detected...",
    "priority": "high",
    "requiresResponse": true
  }
}
```

#### Emergency Events
```json
{
  "type": "emergency_status",
  "data": {
    "emergencyId": "emergency_1703845200_critical",
    "status": "dispatched",
    "estimatedArrival": "45 seconds",
    "message": "Response team approaching location"
  }
}
```

---

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INVITATION_CODE",
    "message": "The provided invitation code is invalid or expired",
    "details": {
      "providedCode": "INVALID2024001",
      "suggestedAction": "Contact your relationship manager for a valid code"
    },
    "timestamp": "2024-06-29T10:30:00Z",
    "requestId": "req_1703845200_abc123"
  }
}
```

### Common Error Codes

#### Authentication Errors
- `INVALID_INVITATION_CODE`: Invitation code is invalid or expired
- `BIOMETRIC_VERIFICATION_FAILED`: Biometric authentication failed
- `DEVICE_NOT_TRUSTED`: Device security assessment failed
- `SESSION_EXPIRED`: User session has expired
- `INSUFFICIENT_PRIVILEGES`: User lacks required permissions

#### Butler AI Errors
- `BUTLER_UNAVAILABLE`: Butler AI service temporarily unavailable
- `INVALID_CONTEXT`: Invalid conversation context provided
- `PROCESSING_TIMEOUT`: AI processing took too long
- `CAPABILITY_DISABLED`: Requested capability is disabled

#### Emergency Service Errors
- `EMERGENCY_SERVICE_UNAVAILABLE`: Emergency service temporarily unavailable
- `INVALID_LOCATION`: Location verification failed
- `RESPONSE_TEAM_BUSY`: No response team available

#### Concierge Errors
- `SERVICE_UNAVAILABLE`: Requested service not available
- `BOOKING_CONFLICT`: Scheduling conflict detected
- `INSUFFICIENT_NOTICE`: Insufficient advance notice for booking
- `PAYMENT_REQUIRED`: Payment authorization required

#### Rate Limiting
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please slow down.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "resetTime": "2024-06-29T11:00:00Z"
    }
  }
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error
- `503`: Service Unavailable

---

*This API documentation covers all endpoints and functionalities of the GridWorks Black Portal system. For additional technical details and implementation examples, refer to the technical architecture documentation.*