# 🚀 API Endpoints Documentation - Unified AI Processor

## ✅ **API Implementation Status: COMPLETE**

The unified AI processor is **fully exposed through REST API endpoints** and ready for UI integration. All functionality is accessible via HTTP requests to your Node.js backend.

## 🌐 **Base URL**
```
http://localhost:3000/api/bigquery-ai
```

## 📋 **Available API Endpoints**

### **1. 🔍 Core Analysis Endpoints**

#### **POST `/api/bigquery-ai/comprehensive-analysis`**
**Description**: Run comprehensive 5-phase supply chain security analysis  
**Request Body**:
```json
{
  "threatId": "THREAT001",           // Optional: Specific threat to analyze
  "queryText": "supply chain breach", // Optional: Natural language query
  "assetIds": ["ASSET001", "ASSET002"] // Optional: Specific assets to analyze
}
```
**Response**:
```json
{
  "success": true,
  "data": {
    "analysis_id": "ANALYSIS_20250829_150012",
    "processing_time": 2.45,
    "results": {
      "ai_sql_analysis": { "status": "success" },
      "vector_analysis": { "status": "success" },
      "multimodal_analysis": { "status": "success" },
      "cross_analysis_correlation": { "status": "success" },
      "comprehensive_report": { "status": "success" }
    }
  },
  "cost_usd": 0.25,
  "processing_time": 2.45
}
```

#### **POST `/api/bigquery-ai/analyze-threat`**
**Description**: Analyze specific threat report using AI  
**Request Body**:
```json
{
  "reportId": "THREAT001"
}
```

#### **POST `/api/bigquery-ai/analyze-vendor`**
**Description**: Analyze vendor using multimodal AI  
**Request Body**:
```json
{
  "vendorId": "V001"
}
```

### **2. 🔍 Vector Processing Endpoints**

#### **POST `/api/bigquery-ai/enhanced-vector-search`**
**Description**: Enhanced vector similarity search  
**Request Body**:
```json
{
  "queryText": "ransomware attack",
  "searchType": "threats",  // "threats", "vendors", "assets"
  "topK": 10
}
```

#### **POST `/api/bigquery-ai/vector-search`**
**Description**: Basic vector similarity search  
**Request Body**:
```json
{
  "reportId": "THREAT001"
}
```

#### **POST `/api/bigquery-ai/generate-embeddings`**
**Description**: Generate embeddings for assets  
**Request Body**:
```json
{
  "assetType": "threats"  // "threats", "vendors", "assets"
}
```

#### **POST `/api/bigquery-ai/create-vector-indexes`**
**Description**: Create vector indexes for similarity search  
**Request Body**: `{}` (no parameters required)

#### **POST `/api/bigquery-ai/semantic-clustering`**
**Description**: Perform semantic clustering analysis  
**Request Body**: `{}` (no parameters required)

### **3. 🏗️ Multimodal Analysis Endpoints**

#### **POST `/api/bigquery-ai/analyze-multimodal-asset`**
**Description**: Analyze multimodal asset (image, document, video)  
**Request Body**:
```json
{
  "assetId": "ASSET001"
}
```

#### **POST `/api/bigquery-ai/upload-and-analyze-asset`**
**Description**: Upload and analyze new asset  
**Request Body**: Multipart form data with asset file

### **4. 🎯 AI SQL Function Endpoints**

#### **POST `/api/bigquery-ai/threat-intelligence`**
**Description**: Generate threat intelligence using AI SQL  
**Request Body**: `{}` (no parameters required)

#### **POST `/api/bigquery-ai/forecast-threats`**
**Description**: Forecast threat metrics using AI.FORECAST  
**Request Body**: `{}` (no parameters required)

#### **POST `/api/bigquery-ai/risk-assessment`**
**Description**: Generate supply chain risk assessment using AI.GENERATE_TABLE  
**Request Body**: `{}` (no parameters required)

#### **POST `/api/bigquery-ai/incident-response`**
**Description**: Generate incident response plan using AI  
**Request Body**: `{}` (no parameters required)

### **5. 📊 Data & Export Endpoints**

#### **POST `/api/bigquery-ai/export-data`**
**Description**: Export AI-enhanced data  
**Request Body**:
```json
{
  "dataType": "threats",  // "threats", "vendors", "analytics"
  "format": "json"        // "json", "csv"
}
```

#### **POST `/api/bigquery-ai/demo`**
**Description**: Run complete AI processing pipeline demo  
**Request Body**: `{}` (no parameters required)

### **6. ⚙️ System & Setup Endpoints**

#### **POST `/api/bigquery-ai/setup`**
**Description**: Setup BigQuery AI environment  
**Request Body**: `{}` (no parameters required)

#### **POST `/api/bigquery-ai/reset-costs`**
**Description**: Reset daily cost tracking  
**Request Body**: `{}` (no parameters required)

### **7. 📊 Status & Monitoring Endpoints**

#### **GET `/api/bigquery-ai/status`**
**Description**: Get BigQuery AI processing status  
**Response**:
```json
{
  "success": true,
  "data": {
    "status": "available",
    "cost_summary": {
      "today": {
        "cost_usd": 0.25,
        "budget_limit_usd": 5.00,
        "remaining_usd": 4.75,
        "usage_percent": 5.0
      }
    },
    "budget_status": "healthy",
    "config": {
      "daily_budget_limit": 5.00,
      "max_query_cost": 1.00,
      "max_processing_mb": 1000,
      "query_timeout": 300
    }
  }
}
```

## 🎯 **UI Integration Examples**

### **React/JavaScript Example**
```javascript
// Run comprehensive analysis
const runAnalysis = async () => {
  try {
    const response = await fetch('/api/bigquery-ai/comprehensive-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        queryText: 'supply chain security threats',
        assetIds: ['ASSET001', 'ASSET002']
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Analysis completed:', result.data);
      console.log('Cost:', result.cost_usd);
      console.log('Processing time:', result.processing_time);
    } else {
      console.error('Analysis failed:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
};

// Get system status
const getStatus = async () => {
  try {
    const response = await fetch('/api/bigquery-ai/status');
    const result = await response.json();
    
    if (result.success) {
      const { cost_summary, budget_status } = result.data;
      console.log('Budget remaining:', cost_summary.today.remaining_usd);
      console.log('System status:', budget_status);
    }
  } catch (error) {
    console.error('Status check failed:', error);
  }
};
```

### **Python Example**
```python
import requests

# Run comprehensive analysis
def run_analysis(query_text, asset_ids=None):
    url = "http://localhost:3000/api/bigquery-ai/comprehensive-analysis"
    payload = {
        "queryText": query_text,
        "assetIds": asset_ids or []
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result["success"]:
        print(f"Analysis completed in {result['processing_time']}s")
        print(f"Cost: ${result['cost_usd']}")
        return result["data"]
    else:
        print(f"Analysis failed: {result['error']}")
        return None

# Get system status
def get_status():
    url = "http://localhost:3000/api/bigquery-ai/status"
    response = requests.get(url)
    result = response.json()
    
    if result["success"]:
        cost_summary = result["data"]["cost_summary"]["today"]
        print(f"Budget remaining: ${cost_summary['remaining_usd']}")
        print(f"Usage: {cost_summary['usage_percent']}%")
        return result["data"]
    else:
        print(f"Status check failed: {result['error']}")
        return None
```

### **cURL Examples**
```bash
# Run comprehensive analysis
curl -X POST http://localhost:3000/api/bigquery-ai/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "queryText": "supply chain breach",
    "assetIds": ["ASSET001"]
  }'

# Get system status
curl http://localhost:3000/api/bigquery-ai/status

# Run threat analysis
curl -X POST http://localhost:3000/api/bigquery-ai/analyze-threat \
  -H "Content-Type: application/json" \
  -d '{"reportId": "THREAT001"}'

# Perform vector search
curl -X POST http://localhost:3000/api/bigquery-ai/enhanced-vector-search \
  -H "Content-Type: application/json" \
  -d '{
    "queryText": "ransomware attack",
    "searchType": "threats",
    "topK": 10
  }'
```

## 🔧 **API Configuration**

### **Environment Variables**
```bash
# Python path for AI processing
PYTHON_PATH=./tools/bigquery_ai/venv/bin/python

# AI processor script path
BIGQUERY_AI_SCRIPT_PATH=./tools/bigquery_ai/unified_ai_processor.py

# API server configuration
PORT=3000
CORS_ORIGIN=http://localhost:3000
RATE_LIMIT_MAX=100
RATE_LIMIT_TIME_WINDOW=60000
```

### **CORS Configuration**
The API is configured with CORS support for frontend integration:
```javascript
// CORS is enabled for localhost:3000 by default
// Can be customized via CORS_ORIGIN environment variable
```

## 📊 **Response Format**

### **Success Response**
```json
{
  "success": true,
  "data": { /* response data */ },
  "cost_usd": 0.25,
  "query_type": "comprehensive_analysis",
  "processing_time": 2.45,
  "metadata": {
    "timestamp": "2025-08-29T15:00:12.000Z",
    "source": "bigquery_ai"
  }
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Comprehensive analysis failed: No module named 'bigframes'"
  },
  "metadata": {
    "timestamp": "2025-08-29T15:00:12.000Z",
    "requestId": "req-123"
  }
}
```

## 🚀 **Production Deployment**

### **1. Start the API Server**
```bash
# Navigate to project root
cd /Users/rahulchaturvedi/Project/Supply\ Chain

# Install dependencies
npm install

# Build the project
npm run build

# Start the server
npm start
```

### **2. Test API Endpoints**
```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test BigQuery AI status
curl http://localhost:3000/api/bigquery-ai/status

# Test comprehensive analysis
curl -X POST http://localhost:3000/api/bigquery-ai/comprehensive-analysis \
  -H "Content-Type: application/json" \
  -d '{"queryText": "test query"}'
```

### **3. UI Integration**
Your frontend can now make HTTP requests to any of the available endpoints. The API provides:
- ✅ **RESTful endpoints** for all AI operations
- ✅ **JSON request/response** format
- ✅ **CORS support** for frontend integration
- ✅ **Error handling** with detailed error codes
- ✅ **Cost tracking** for all operations
- ✅ **Progress monitoring** for long-running operations

## 🎉 **Conclusion**

The **unified AI processor is fully exposed through a comprehensive REST API** and ready for UI integration. All functionality is accessible via HTTP endpoints, providing:

1. **🎯 Complete API Coverage** - All AI operations exposed via REST
2. **💰 Cost Management** - Real-time cost tracking and budget control
3. **🔧 Production Ready** - Error handling, rate limiting, and monitoring
4. **📱 UI Ready** - CORS enabled, JSON responses, comprehensive endpoints
5. **📊 Status Monitoring** - Real-time system status and cost information

Your UI can now seamlessly integrate with all the unified AI processor capabilities through simple HTTP requests! 🚀
