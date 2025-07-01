# Quick Start Guide

> **Get your AI-powered trading platform running in 30 minutes**

This guide will help you integrate GridWorks AI SDK Suite into your trading platform, broker system, or fintech application quickly and efficiently.

## 🚀 **Overview**

GridWorks AI SDK Suite provides three core services:

1. **🛡️ AI Support** - Instant trading support with WhatsApp integration
2. **🌍 AI Intelligence** - Global market intelligence and trade ideas
3. **👥 AI Moderator** - Expert community management and revenue sharing

## 📋 **Prerequisites**

Before you begin, ensure you have:

- [ ] **API Key** from [GridWorks Dashboard](https://dashboard.gridworks.ai)
- [ ] **Node.js 16+** or **Python 3.8+** installed
- [ ] **Trading platform** or **broker system** to integrate with
- [ ] **Basic understanding** of REST APIs

## ⚡ **30-Minute Quick Start**

### **Step 1: Get API Credentials (5 minutes)**

1. **Sign up** at [dashboard.gridworks.ai](https://dashboard.gridworks.ai)
2. **Create new project** for your integration
3. **Copy API key** and **client credentials**
4. **Choose your tier** (start with Pro for full features)

```json
{
  "client_id": "gw_client_abc123",
  "api_key": "gw_api_xyz789",
  "tier": "pro",
  "services": ["support", "intelligence", "moderator"]
}
```

### **Step 2: Install SDK (2 minutes)**

Choose your preferred language:

#### **JavaScript/TypeScript**
```bash
npm install @gridworks/ai-sdk-suite
# or
yarn add @gridworks/ai-sdk-suite
```

#### **Python**
```bash
pip install gridworks-ai-sdk
```

#### **REST API (no SDK)**
```bash
# Direct API calls - no installation needed
curl https://api.gridworks.ai/v1/health
```

### **Step 3: Initialize SDK (3 minutes)**

#### **JavaScript Example**
```javascript
import { GridWorksSDK } from '@gridworks/ai-sdk-suite';

const sdk = new GridWorksSDK({
  clientId: 'gw_client_abc123',
  apiKey: 'gw_api_xyz789',
  services: ['support', 'intelligence', 'moderator'],
  tier: 'pro',
  integrationSettings: {
    whatsappDelivery: true,
    multiLanguage: true,
    revenueSharing: true
  }
});

// Initialize all services
await sdk.initialize();
console.log('GridWorks AI SDK ready!');
```

#### **Python Example**
```python
from gridworks_sdk import GridWorksSDK

sdk = GridWorksSDK(
    client_id='gw_client_abc123',
    api_key='gw_api_xyz789',
    services=['support', 'intelligence', 'moderator'],
    tier='pro'
)

# Initialize all services
await sdk.initialize()
print('GridWorks AI SDK ready!')
```

### **Step 4: Implement Core Features (20 minutes)**

#### **A. AI Support Integration (7 minutes)**

Enable instant AI-powered support for your users:

```javascript
// Handle user support queries
async function handleUserQuery(userId, query, context) {
  const response = await sdk.support.query({
    userId: userId,
    message: query,
    context: {
      balance: context.balance,
      portfolio: context.portfolio,
      recentOrders: context.recentOrders
    },
    language: context.language || 'english',
    deliveryChannels: ['app', 'whatsapp']
  });
  
  return {
    success: response.success,
    message: response.message,
    actions: response.actions,
    responseTime: response.responseTime,
    voiceNoteUrl: response.voiceNoteUrl // If WhatsApp enabled
  };
}

// Example usage
const supportResult = await handleUserQuery(
  'user_123',
  'Why did my order for RELIANCE fail?',
  {
    balance: 50000,
    portfolio: 'aggressive',
    recentOrders: ['RELIANCE_BUY_2450'],
    language: 'hindi'
  }
);

console.log(`AI Response: ${supportResult.message}`);
console.log(`Response Time: ${supportResult.responseTime}ms`);
```

#### **B. Morning Intelligence Integration (8 minutes)**

Provide daily market intelligence to your users:

```javascript
// Generate morning pulse for users
async function getMorningIntelligence(userId, userTier) {
  const pulse = await sdk.intelligence.getMorningPulse({
    userId: userId,
    userTier: userTier,
    deliveryChannels: ['app', 'whatsapp'],
    language: 'english',
    includeVoiceNote: userTier !== 'lite'
  });
  
  return {
    summary: pulse.content.summary,
    tradeIdeas: pulse.content.tradeIdeas,
    voiceNoteUrl: pulse.voiceNoteUrl,
    correlationInsights: pulse.content.correlationInsights,
    institutionalData: pulse.content.institutionalIntelligence // Black tier only
  };
}

// Schedule morning pulse delivery
async function scheduleDaily MorningPulse() {
  const users = await getActiveUsers(); // Your user database
  
  for (const user of users) {
    const intelligence = await getMorningIntelligence(user.id, user.tier);
    
    // Send to your frontend
    await sendToUserDashboard(user.id, intelligence);
    
    // Send WhatsApp voice note (Pro+ tiers)
    if (user.tier !== 'lite' && intelligence.voiceNoteUrl) {
      await sendWhatsAppVoiceNote(user.phone, intelligence.voiceNoteUrl);
    }
  }
}

// Set up daily schedule (7:30 AM IST)
setInterval(scheduleDailyMorningPulse, 24 * 60 * 60 * 1000);
```

#### **C. Expert Group Moderation (5 minutes)**

Enable expert communities with AI moderation:

```javascript
// Create expert group with AI moderation
async function createExpertGroup(expertId, groupSettings) {
  const group = await sdk.moderator.createExpertGroup({
    expertId: expertId,
    groupConfig: {
      name: groupSettings.name,
      description: groupSettings.description,
      subscriptionPrice: groupSettings.price,
      maxMembers: groupSettings.maxMembers,
      category: groupSettings.category
    },
    expertVerification: {
      required: true,
      zkProofEnabled: true
    },
    aiModeration: {
      spamDetection: true,
      autoModeration: true,
      confidenceThreshold: 0.8
    },
    revenueSharing: {
      expertShare: getExpertShareByTier(expertTier), // 60-85% based on tier
      platformShare: getPlatformShare(expertTier)    // 15-40% based on tier
    }
  });
  
  return group;
}

// Moderate group messages in real-time
async function moderateGroupMessage(groupId, message) {
  const moderation = await sdk.moderator.moderateMessage({
    groupId: groupId,
    message: {
      userId: message.userId,
      content: message.content,
      timestamp: message.timestamp
    }
  });
  
  // Handle moderation result
  if (moderation.action === 'block') {
    await blockMessage(message.id);
    await notifyModerators(groupId, moderation.reason);
  } else if (moderation.action === 'flag') {
    await flagForHumanReview(message.id, moderation.reason);
  }
  
  return moderation;
}
```

## 🎯 **Essential Integrations**

### **User Authentication Integration**

```javascript
// Link your user system with GridWorks tiers
async function syncUserWithGridWorks(userId, userTier) {
  await sdk.setUserContext(userId, {
    tier: userTier,
    permissions: getTierPermissions(userTier),
    quotas: getTierQuotas(userTier)
  });
}

function getTierPermissions(tier) {
  const permissions = {
    lite: ['support_basic', 'intelligence_teaser'],
    pro: ['support_unlimited', 'intelligence_full', 'groups_participant'],
    elite: ['support_butler', 'intelligence_personalized', 'groups_creator'],
    black: ['support_institutional', 'intelligence_institutional', 'groups_admin']
  };
  
  return permissions[tier] || permissions.lite;
}
```

### **WhatsApp Business Integration**

```javascript
// Enable WhatsApp delivery for your platform
async function setupWhatsAppIntegration() {
  await sdk.enableWhatsAppDelivery({
    businessAccountId: 'your_whatsapp_business_id',
    phoneNumber: '+91XXXXXXXXXX',
    webhookUrl: 'https://your-platform.com/webhooks/whatsapp',
    deliveryTypes: ['support_responses', 'morning_pulse', 'trade_alerts']
  });
}

// Handle incoming WhatsApp messages
app.post('/webhooks/whatsapp', async (req, res) => {
  const message = req.body;
  
  if (message.type === 'text') {
    const response = await sdk.support.processWhatsAppQuery({
      phoneNumber: message.from,
      message: message.text,
      context: await getUserContext(message.from)
    });
    
    await sendWhatsAppResponse(message.from, response);
  }
  
  res.sendStatus(200);
});
```

## 📊 **Testing Your Integration**

### **1. Test AI Support**

```javascript
// Test different user scenarios
const testCases = [
  {
    query: "Why did my order fail?",
    expectedResponse: "order_failure_analysis",
    tier: "pro"
  },
  {
    query: "मेरा पोर्टफोलियो कैसा चल रहा है?", // Hindi
    expectedResponse: "portfolio_analysis",
    tier: "elite"
  }
];

for (const test of testCases) {
  const result = await sdk.support.query({
    message: test.query,
    userTier: test.tier
  });
  
  console.log(`✅ ${test.query} → ${result.success}`);
}
```

### **2. Test Morning Pulse**

```javascript
// Test intelligence generation
const morningPulse = await sdk.intelligence.getMorningPulse({
  userTier: 'pro',
  language: 'english'
});

console.log('Trade Ideas:', morningPulse.content.tradeIdeas.length);
console.log('Voice Note:', morningPulse.voiceNoteUrl ? '✅' : '❌');
```

### **3. Test Expert Group Moderation**

```javascript
// Test spam detection
const spamTest = await sdk.moderator.moderateMessage({
  groupId: 'test_group',
  message: {
    content: '🔥🔥 GUARANTEED PROFIT!!! Call 9999999999 🔥🔥',
    userId: 'test_user'
  }
});

console.log('Spam detected:', spamTest.action === 'block'); // Should be true
```

## 🚀 **Go Live Checklist**

Before deploying to production:

- [ ] **API Keys**: Production keys configured
- [ ] **Webhook Endpoints**: All webhooks tested and secured
- [ ] **Error Handling**: Graceful fallbacks implemented
- [ ] **Rate Limiting**: Respect SDK rate limits
- [ ] **User Permissions**: Tier-based access controls
- [ ] **WhatsApp Business**: Business verification completed
- [ ] **Monitoring**: Health checks and alerts configured
- [ ] **Documentation**: Internal docs for your team

## 🎯 **Next Steps**

Congratulations! You now have a basic GridWorks AI SDK integration. Here's what to explore next:

### **Immediate (Week 1)**
- ✅ [Implement tier progression logic](../tier-integration/tier-progression.md)
- ✅ [Set up intelligent upselling](../tier-integration/intelligent-upselling.md)
- ✅ [Configure monitoring and alerts](../advanced/monitoring.md)

### **Short Term (Month 1)**
- ✅ [Create expert revenue sharing](../business-models/expert-revenue.md)
- ✅ [Implement advanced analytics](../advanced/monitoring.md)
- ✅ [Add custom AI training](../advanced/customization.md)

### **Long Term (Quarter 1)**
- ✅ [Scale to enterprise features](../deployment/infrastructure.md)
- ✅ [Launch B2B SDK offering](../business-models/b2b-licensing.md)
- ✅ [Implement international expansion](../advanced/internationalization.md)

## 🆘 **Need Help?**

### **Common Issues**
- 🔍 [Troubleshooting Guide](../support/troubleshooting.md)
- ❓ [Frequently Asked Questions](../support/faq.md)

### **Get Support**
- 💬 **Discord**: [Join our developer community](https://discord.gg/gridworks)
- 📧 **Email**: support@gridworks.ai
- 📞 **Phone**: +91-80-4096-7890 (Enterprise customers)

### **Resources**
- 📖 [Complete API Documentation](../api-reference/rest-api.md)
- 🎥 [Video Tutorials](https://youtube.com/gridworks-ai)
- 📊 [Example Applications](../examples/trading-platform.md)

---

**🎉 Congratulations on integrating GridWorks AI SDK Suite!**

Your trading platform now has enterprise-grade AI capabilities. Start exploring advanced features and join our community of innovative fintech builders.

**[Explore Advanced Features →](../services/ai-support/README.md)** | **[Join Discord Community →](https://discord.gg/gridworks)** | **[Schedule Demo →](mailto:demo@gridworks.ai)**