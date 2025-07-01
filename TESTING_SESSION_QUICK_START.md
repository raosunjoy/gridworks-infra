# GridWorks Testing Session - Quick Start Guide

**🚨 IMMEDIATE NEXT SESSION FOCUS: TESTING & DEPLOYMENT**

## 🎯 **CRITICAL PRIORITY: START WITH THESE COMMANDS**

### **1. Backend Server Deployment (FIRST)**
```bash
# Navigate to project root
cd /path/to/GridWorks-Infra

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Verify backend is running
curl http://localhost:8000/health
open http://localhost:8000/docs
```

### **2. Enterprise Portal Deployment (SECOND)**
```bash
# Navigate to portal directory
cd partners-portal

# Install Node.js dependencies
npm install

# Create environment file
cp .env.example .env.local

# Configure OAuth and Stripe keys in .env.local
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# STRIPE_SECRET_KEY=...
# NEXTAUTH_SECRET=...

# Start Next.js development server
npm run dev

# Verify portal is running
open http://localhost:3001
```

### **3. Test Implementation Setup (THIRD)**
```bash
# Install testing dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Create test configuration
touch jest.config.js
touch jest.setup.js

# Create test directories
mkdir -p src/__tests__/{store,auth,pages,components,integration,e2e}
mkdir -p src/__tests__/{mocks,fixtures,setup}
```

## 🧪 **CRITICAL TESTING AREAS (IMPLEMENT FIRST)**

### **Phase 1: Zustand Store Testing (Day 1)**
```bash
# PRIORITY 1: Core state management
src/__tests__/store/store.test.ts
src/__tests__/store/auth-store.test.ts
src/__tests__/store/organization-store.test.ts
src/__tests__/store/pricing-store.test.ts
```

### **Phase 2: OAuth Authentication (Day 1-2)**
```bash
# PRIORITY 2: Authentication flows
src/__tests__/auth/oauth.test.ts
src/__tests__/auth/session.test.ts
src/__tests__/auth/permissions.test.ts
```

### **Phase 3: Critical UI Components (Day 2-3)**
```bash
# PRIORITY 3: Essential page components
src/__tests__/pages/dashboard.test.tsx
src/__tests__/pages/admin.test.tsx
src/__tests__/pages/api-keys.test.tsx
src/__tests__/pages/billing.test.tsx
```

## 🔍 **MANUAL TESTING CHECKLIST**

### **CRITICAL USER FLOWS TO TEST:**
- [ ] **Enterprise Sign-Up**: OAuth → Organization Setup → Plan Selection → Payment
- [ ] **API Key Generation**: Dashboard → API Keys → Create → Test in Sandbox
- [ ] **Admin Management**: Admin Portal → Users → Organizations → Analytics
- [ ] **Developer Integration**: Sandbox → Code Examples → API Testing
- [ ] **Billing Workflow**: Pricing → Stripe → Subscription → Invoices

### **SYSTEMS TO VERIFY:**
- [ ] **Backend APIs**: All 4 B2B services responding (AI, Anonymous, Trading, Banking)
- [ ] **Portal Pages**: All 10 pages loading and functional
- [ ] **OAuth Providers**: Google, Microsoft authentication working
- [ ] **Stripe Integration**: Payment processing and webhooks
- [ ] **AI Chat Widget**: Context-aware responses and suggestions

## 🚨 **EXPECTED ISSUES & QUICK FIXES**

### **Common Problems:**
1. **OAuth Redirect Issues**: Check callback URLs in provider settings
2. **CORS Errors**: Add proper headers in backend FastAPI
3. **Stripe Webhook Failures**: Verify webhook endpoints and secrets
4. **API Key Validation**: Check format and permissions in backend
5. **State Persistence**: Verify Zustand storage configuration

### **Quick Debug Commands:**
```bash
# Check backend logs
tail -f logs/fastapi.log

# Check portal console
# Open browser dev tools → Console

# Verify environment variables
echo $GOOGLE_CLIENT_ID
cat .env.local

# Test API connectivity
curl -H "Authorization: Bearer test_key" http://localhost:8000/ai-suite/health
```

## 📊 **SUCCESS METRICS - TRACK THESE**

### **Test Coverage Goals:**
- [ ] **Zustand Store**: 100% coverage
- [ ] **OAuth Authentication**: 100% coverage  
- [ ] **API Key Management**: 100% coverage
- [ ] **Stripe Integration**: 100% coverage
- [ ] **UI Components**: 100% coverage

### **Manual Testing Goals:**
- [ ] **Complete User Onboarding**: Enterprise client can sign up end-to-end
- [ ] **API Integration Working**: Developers can generate keys and test APIs
- [ ] **Admin Functionality**: Admins can manage organizations and users
- [ ] **Payment Processing**: Stripe subscriptions working correctly
- [ ] **Performance**: Portal loads <3 seconds, APIs respond <1 second

## 🎯 **SESSION END GOAL**

**OUTCOME**: Production-ready GridWorks B2B Infrastructure Platform with:
- ✅ 100% test coverage
- ✅ All servers deployed and functional
- ✅ Complete manual testing validation
- ✅ Zero critical bugs in core workflows
- ✅ Ready for Fortune 500 client deployment

**VALUE**: Transform ₹60,000Cr platform from development to production-ready!

---

**⚡ START IMMEDIATELY WITH BACKEND DEPLOYMENT, THEN PORTAL, THEN TESTING!**