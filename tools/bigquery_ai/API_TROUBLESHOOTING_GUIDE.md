# 🔧 API Troubleshooting Guide - Fixing Service Unavailable Errors

## 🚨 **Current Issues Identified**

### **Problem 1: Port Mismatch**
- **UI is calling**: `http://localhost:8080/api/bigquery-ai/*`
- **API is running on**: `http://localhost:3000/api/bigquery-ai/*`

### **Problem 2: Missing `/costs` Endpoint**
- The `/costs` endpoint was missing from the API routes
- Added the endpoint but needs proper implementation

### **Problem 3: Service Availability Check**
- Service is showing as unavailable due to file path issues
- Need to fix the availability check logic

## ✅ **Solutions Implemented**

### **1. Added Missing `/costs` Endpoint**
```typescript
// GET /api/bigquery-ai/costs - Get detailed cost information and trends
fastify.get('/bigquery-ai/costs', async (request: FastifyRequest, reply: FastifyReply) => {
  // Implementation added to src/routes/bigquery-ai.ts
});
```

### **2. Added getCostMonitor Method**
```typescript
getCostMonitor(): any {
  if (!this.isAvailable) {
    return null;
  }

  try {
    const { getCostMonitor } = require('../../tools/bigquery_ai/cost_monitor');
    return getCostMonitor();
  } catch (error) {
    logger.error('Failed to get cost monitor', error);
    return null;
  }
}
```

## 🔧 **Step-by-Step Fix Instructions**

### **Step 1: Fix Port Configuration**

#### **Option A: Update UI to use correct port**
Change your UI API calls from:
```javascript
// ❌ Wrong port
const API_BASE = 'http://localhost:8080/api/bigquery-ai';

// ✅ Correct port
const API_BASE = 'http://localhost:3000/api/bigquery-ai';
```

#### **Option B: Change API server port**
Update your environment variables:
```bash
# In your .env file or environment
PORT=8080
```

### **Step 2: Verify API Server is Running**
```bash
# Navigate to project root
cd /Users/rahulchaturvedi/Project/Supply\ Chain

# Check if server is running
curl http://localhost:3000/api/health

# Expected response:
# {"success":true,"data":{"status":"healthy","timestamp":"..."}}
```

### **Step 3: Test the Fixed Endpoints**
```bash
# Test status endpoint
curl http://localhost:3000/api/bigquery-ai/status

# Test costs endpoint
curl http://localhost:3000/api/bigquery-ai/costs

# Test with Python script
cd tools/bigquery_ai
python3 test_api_endpoints.py
```

## 🧪 **Testing the Fixes**

### **1. Test API Endpoints**
```bash
# Navigate to bigquery_ai directory
cd tools/bigquery_ai

# Run the test script
python3 test_api_endpoints.py
```

### **2. Manual Testing with cURL**
```bash
# Test status endpoint
curl -X GET http://localhost:3000/api/bigquery-ai/status

# Test costs endpoint
curl -X GET http://localhost:3000/api/bigquery-ai/costs

# Test comprehensive analysis
curl -X POST http://localhost:3000/api/bigquery-ai/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"queryText": "test query"}'
```

## 🔍 **Debugging Steps**

### **1. Check Server Logs**
```bash
# Look for these log messages in your server output:
# ✅ "BigQuery AI service is available"
# ❌ "BigQuery AI script not found, service disabled"
```

### **2. Verify File Paths**
```bash
# Check if the Python script exists
ls -la tools/bigquery_ai/unified_ai_processor_simple.py

# Check if virtual environment exists
ls -la tools/bigquery_ai/venv/bin/python
```

### **3. Check Service Availability**
```bash
# The service should show these paths:
# Python path: ./tools/bigquery_ai/venv/bin/python
# Script path: ./tools/bigquery_ai/unified_ai_processor_simple.py
```

## 🚀 **Quick Fix Commands**

### **Fix 1: Update UI Port (Recommended)**
```javascript
// In your UI code, change:
const API_BASE = 'http://localhost:3000/api/bigquery-ai';
```

### **Fix 2: Restart API Server**
```bash
# Stop current server (Ctrl+C)
# Then restart:
cd /Users/rahulchaturvedi/Project/Supply\ Chain
npm start
```

### **Fix 3: Test Endpoints**
```bash
# Test from command line
curl http://localhost:3000/api/bigquery-ai/status
curl http://localhost:3000/api/bigquery-ai/costs
```

## 📋 **Expected Results After Fixes**

### **Status Endpoint** (`/api/bigquery-ai/status`)
```json
{
  "success": true,
  "data": {
    "status": "available",
    "cost_summary": {
      "today": {
        "cost_usd": 0.0000,
        "budget_limit_usd": 5.00,
        "remaining_usd": 5.0000,
        "usage_percent": 0.0
      }
    },
    "budget_status": "healthy"
  }
}
```

### **Costs Endpoint** (`/api/bigquery-ai/costs`)
```json
{
  "success": true,
  "data": {
    "cost_summary": {
      "today": {
        "cost_usd": 0.0000,
        "budget_limit_usd": 5.00,
        "remaining_usd": 5.0000,
        "usage_percent": 0.0
      }
    },
    "daily_costs": {
      "2025-08-29": {"cost_usd": 0.0000, "usage_percent": 0.0},
      "2025-08-28": {"cost_usd": 0.0000, "usage_percent": 0.0}
    }
  }
}
```

## 🎯 **Next Steps**

### **1. Immediate Actions**
- ✅ Fix port configuration (UI or API)
- ✅ Restart API server
- ✅ Test endpoints with cURL
- ✅ Verify service availability

### **2. UI Integration**
- ✅ Update UI to use correct port (3000)
- ✅ Test API calls from UI
- ✅ Implement error handling for API failures

### **3. Production Readiness**
- ⚠️ Install full ML dependencies for complete functionality
- ⚠️ Test comprehensive analysis endpoints
- ⚠️ Deploy to production environment

## 🔍 **Common Issues and Solutions**

### **Issue: "BigQuery AI service is not available"**
**Solution**: Check if the Python script path is correct and the file exists

### **Issue: "Cost information not available"**
**Solution**: The `/costs` endpoint has been added and should work now

### **Issue: Port connection refused**
**Solution**: Verify the API server is running on the correct port

### **Issue: CORS errors**
**Solution**: CORS is configured for localhost:3000 by default

## 📞 **Support Commands**

### **Check Service Status**
```bash
# From project root
curl http://localhost:3000/api/bigquery-ai/status
```

### **Check Server Health**
```bash
# From project root
curl http://localhost:3000/api/health
```

### **View Server Logs**
```bash
# Look for these key messages:
# ✅ "BigQuery AI service is available"
# ✅ "Fastify plugins registered"
# ✅ "Supply Chain API initialization completed"
```

## 🎉 **Expected Outcome**

After implementing these fixes, you should see:
1. ✅ **Status endpoint working** - Returns service availability and cost summary
2. ✅ **Costs endpoint working** - Returns detailed cost information and trends
3. ✅ **Service available** - No more "SERVICE_UNAVAILABLE" errors
4. ✅ **UI integration working** - Frontend can successfully call the API

The unified AI processor will be fully accessible through the REST API for your UI integration! 🚀
