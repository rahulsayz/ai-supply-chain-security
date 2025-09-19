# 🚀 Live BigQuery AI Analysis - API Documentation

## 🎯 **Overview**

The Live BigQuery AI Analysis system provides **real-time, on-demand AI processing** for supply chain threat detection and vendor risk assessment. This system leverages Google BigQuery's AI/ML capabilities to deliver instant insights and risk assessments.

## 🔗 **Base URL**
```
http://localhost:8080/api/bigquery-ai
```

---

## 📡 **1. Live Analysis Endpoint**

### **POST** `/live-analysis`
**Real-time BigQuery AI analysis with live streaming updates**

#### **Purpose**
Performs comprehensive AI analysis with real-time progress updates, cost monitoring, and step-by-step feedback.

#### **Request Body**
```json
{
  "vendorId": "V001",           // Optional: Specific vendor to analyze
  "threatId": "RPT001",         // Optional: Specific threat report to analyze
  "analysisType": "comprehensive", // "quick" or "comprehensive"
  "queryText": "supply chain security threats", // Optional: Natural language query
  "assetIds": ["asset1", "asset2"] // Optional: Specific assets to analyze
}
```

#### **Response Format: Server-Sent Events (SSE)**
The endpoint returns a **streaming response** with real-time updates:

```javascript
// Example EventSource usage
const eventSource = new EventSource('/api/bigquery-ai/live-analysis');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'status':
      console.log('Status:', data.message);
      break;
      
    case 'step_start':
      console.log(`Step ${data.stepNumber}/${data.totalSteps}: ${data.message}`);
      break;
      
    case 'step_complete':
      console.log(`Step completed: ${data.message}`);
      console.log(`Progress: ${data.progress}%`);
      console.log(`Current cost: $${data.cost_usd}`);
      break;
      
    case 'analysis_complete':
      console.log('Analysis completed!', data.results);
      break;
      
    case 'error':
      console.error('Analysis failed:', data.message);
      break;
      
    case 'end':
      eventSource.close();
      break;
  }
};
```

#### **Event Types**

##### **1. Status Event**
```json
{
  "type": "status",
  "message": "Starting Live BigQuery AI Analysis...",
  "timestamp": "2025-08-29T10:45:00.000Z",
  "step": "initialization"
}
```

##### **2. Step Start Event**
```json
{
  "type": "step_start",
  "step": "ai_processing",
  "message": "Running BigQuery AI models...",
  "timestamp": "2025-08-29T10:45:01.000Z",
  "stepNumber": 2,
  "totalSteps": 6
}
```

##### **3. Step Complete Event**
```json
{
  "type": "step_complete",
  "step": "ai_processing",
  "message": "Running BigQuery AI models... - Completed",
  "timestamp": "2025-08-29T10:45:03.000Z",
  "stepNumber": 2,
  "totalSteps": 6,
  "cost_usd": 0.002,
  "progress": 33.33
}
```

##### **4. Analysis Complete Event**
```json
{
  "type": "analysis_complete",
  "message": "Live BigQuery AI Analysis completed successfully",
  "timestamp": "2025-08-29T10:45:08.000Z",
  "results": {
    "vendorId": "V001",
    "threatId": "RPT001",
    "analysisType": "comprehensive",
    "ai_insights": {
      "threat_patterns": [
        {
          "pattern": "supply_chain_compromise",
          "confidence": 0.85,
          "risk_level": "high"
        }
      ],
      "risk_assessment": {
        "overall_risk_score": 7.2,
        "risk_level": "medium",
        "confidence": 0.78,
        "factors": ["vendor_security_posture", "threat_intelligence"]
      },
      "recommendations": [
        "Implement enhanced vendor security assessments",
        "Deploy real-time threat monitoring"
      ]
    },
    "processing_metadata": {
      "total_steps": 6,
      "processing_time_ms": 8000,
      "cost_usd": 0.006,
      "ai_models_used": [
        "AI.GENERATE_TABLE",
        "VECTOR_SEARCH",
        "ML.PREDICT_LINEAR_REG",
        "ObjectRef Analysis"
      ]
    }
  }
}
```

#### **Processing Steps**
1. **Data Preparation** - Preparing data for AI analysis
2. **AI Processing** - Running BigQuery AI models
3. **Vector Search** - Performing vector similarity search
4. **Pattern Analysis** - Analyzing threat patterns
5. **Risk Assessment** - Generating risk assessment
6. **Insights Generation** - Generating AI insights

---

## ⚡ **2. Quick Analysis Endpoint**

### **POST** `/quick-analysis`
**Fast threat/vendor analysis for immediate insights**

#### **Purpose**
Provides quick analysis results without real-time streaming, ideal for simple queries and basic risk assessments.

#### **Request Body**
```json
{
  "vendorId": "V001",           // Optional: Vendor to analyze
  "threatId": "RPT001",         // Optional: Threat report to analyze
  "queryText": "vendor security risks" // Optional: Natural language query
}
```

#### **Response**
```json
{
  "success": true,
  "data": {
    "analysis_type": "quick",
    "vendor_id": "V001",
    "threat_id": "RPT001",
    "query_text": "vendor security risks",
    "results": { /* analysis results */ },
    "processing_time": 1500,
    "cost_estimate": 0.00015
  },
  "metadata": {
    "timestamp": "2025-08-29T10:45:00.000Z",
    "source": "bigquery_ai",
    "processingTime": 1500
  }
}
```

---

## 📊 **3. Analysis Status Endpoint**

### **GET** `/analysis-status/:analysisId`
**Get real-time status of ongoing analysis**

#### **Purpose**
Check the status and progress of a running analysis operation.

#### **Response**
```json
{
  "success": true,
  "data": {
    "analysis_id": "analysis_123",
    "status": "in_progress",
    "progress": 66,
    "current_step": "pattern_analysis",
    "total_steps": 6,
    "estimated_completion": "2025-08-29T10:45:05.000Z",
    "cost_usd": 0.004,
    "results_available": false
  },
  "metadata": {
    "timestamp": "2025-08-29T10:45:02.000Z",
    "source": "bigquery_ai",
    "processingTime": 0
  }
}
```

---

## 🔍 **4. Existing Analysis Endpoints**

### **Threat Analysis**
- **POST** `/analyze-threat` - Analyze specific threat reports
- **POST** `/threat-intelligence` - Generate threat intelligence
- **POST** `/forecast-threats` - Predict future threat metrics

### **Vendor Analysis**
- **POST** `/analyze-vendor` - Analyze vendor risk factors
- **POST** `/risk-assessment` - Generate comprehensive risk assessments

### **AI Processing**
- **POST** `/comprehensive-analysis` - Full AI analysis pipeline
- **POST** `/enhanced-vector-search` - Advanced similarity search
- **POST** `/semantic-clustering` - Pattern clustering analysis

---

## 💰 **Cost Management**

### **Real-Time Cost Tracking**
- **Cost per step**: $0.001 per processing step
- **Total analysis cost**: Typically $0.006 for comprehensive analysis
- **Cost updates**: Real-time cost updates during processing
- **Budget limits**: Automatic stopping when approaching budget limits

### **Cost Estimation**
```json
{
  "cost_estimate": 0.064,
  "cost_breakdown": {
    "ai_processing": 0.016,
    "vector_search": 0.012,
    "pattern_analysis": 0.008,
    "risk_assessment": 0.012,
    "data_processing": 0.008,
    "insights_generation": 0.008
  }
}
```

---

## 🎨 **UI Integration Examples**

### **1. React Component for Live Analysis**
```jsx
import React, { useState, useEffect } from 'react';

const LiveAnalysis = ({ vendorId, threatId, queryText }) => {
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [cost, setCost] = useState(0);
  const [results, setResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const startAnalysis = async () => {
    setIsRunning(true);
    
    const eventSource = new EventSource(`/api/bigquery-ai/live-analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ vendorId, threatId, queryText })
    });

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch(data.type) {
        case 'status':
          setStatus(data.message);
          break;
        case 'step_complete':
          setProgress(data.progress);
          setCost(data.cost_usd);
          break;
        case 'analysis_complete':
          setResults(data.results);
          setIsRunning(false);
          eventSource.close();
          break;
      }
    };
  };

  return (
    <div>
      <button onClick={startAnalysis} disabled={isRunning}>
        Start Live Analysis
      </button>
      
      {isRunning && (
        <div>
          <p>Status: {status}</p>
          <progress value={progress} max="100" />
          <p>Progress: {progress}%</p>
          <p>Cost: ${cost}</p>
        </div>
      )}
      
      {results && (
        <div>
          <h3>Analysis Results</h3>
          <p>Risk Score: {results.ai_insights.risk_assessment.overall_risk_score}</p>
          <p>Risk Level: {results.ai_insights.risk_assessment.risk_level}</p>
        </div>
      )}
    </div>
  );
};
```

### **2. JavaScript EventSource Usage**
```javascript
function performLiveAnalysis(params) {
  const eventSource = new EventSource('/api/bigquery-ai/live-analysis');
  
  eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    // Update UI based on event type
    updateProgress(data);
    updateCost(data);
    updateStatus(data);
    
    if (data.type === 'analysis_complete') {
      displayResults(data.results);
      eventSource.close();
    }
  };
  
  eventSource.onerror = function(error) {
    console.error('EventSource failed:', error);
    eventSource.close();
  };
}
```

---

## 🚨 **Error Handling**

### **Common Error Responses**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMS",
    "message": "At least one of vendorId, threatId, queryText, or assetIds must be provided"
  },
  "metadata": {
    "timestamp": "2025-08-29T10:45:00.000Z",
    "requestId": "req-123"
  }
}
```

### **Error Codes**
- `INVALID_PARAMS` - Missing or invalid parameters
- `ANALYSIS_FAILED` - Analysis processing failed
- `SERVICE_UNAVAILABLE` - BigQuery AI service unavailable
- `BUDGET_EXCEEDED` - Analysis stopped due to budget limits
- `TIMEOUT` - Analysis exceeded time limits

---

## 🔧 **Configuration & Limits**

### **Processing Limits**
- **Maximum processing time**: 30 seconds
- **Maximum steps**: 10 processing steps
- **Cost limit**: $0.01 per analysis (configurable)
- **Concurrent analyses**: 5 simultaneous analyses

### **Performance Tuning**
- **Quick analysis**: 2-5 seconds, $0.008-0.024
- **Comprehensive analysis**: 8-15 seconds, $0.048-0.064
- **Real-time updates**: Every 1-2 seconds
- **Progress granularity**: 1% increments

### **AI Confidence Scores**
- **Enterprise-grade AI models** with 85-95% confidence
- **High-quality threat detection** using BigQuery AI functions
- **Reliable risk assessments** for production use

---

## 📱 **Mobile & Responsive Support**

### **Mobile-Optimized Responses**
- **Reduced data payload** for mobile devices
- **Simplified progress updates** for small screens
- **Touch-friendly status indicators**
- **Offline progress caching**

---

## 🎯 **Best Practices**

### **1. User Experience**
- **Show real-time progress** with visual indicators
- **Display cost updates** during processing
- **Provide step-by-step feedback** for transparency
- **Handle errors gracefully** with user-friendly messages

### **2. Performance**
- **Use EventSource** for real-time updates
- **Implement retry logic** for failed connections
- **Cache analysis results** for repeated queries
- **Optimize payload size** for mobile devices

### **3. Cost Management**
- **Show cost estimates** before starting analysis
- **Display real-time cost updates** during processing
- **Implement budget alerts** when approaching limits
- **Provide cost optimization suggestions**

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **WebSocket support** for bi-directional communication
- **Analysis queuing** for high-demand scenarios
- **Batch processing** for multiple analyses
- **Advanced cost optimization** algorithms
- **Machine learning model selection** based on query type

---

## 📞 **Support & Troubleshooting**

### **Common Issues**
1. **Connection drops** - Implement automatic reconnection
2. **High latency** - Use quick analysis for simple queries
3. **Cost overruns** - Set budget limits and monitor usage
4. **Analysis failures** - Check BigQuery service status

### **Debug Information**
- **Request IDs** for tracking issues
- **Processing timestamps** for performance analysis
- **Step-by-step logs** for troubleshooting
- **Cost breakdowns** for optimization

---

## 🎉 **Summary**

The Live BigQuery AI Analysis system provides:

✅ **Real-time processing** with live updates  
✅ **Cost monitoring** during analysis  
✅ **Step-by-step progress** tracking  
✅ **Multiple analysis types** (quick/comprehensive)  
✅ **Comprehensive error handling**  
✅ **Mobile-optimized responses**  
✅ **Budget management** and cost optimization  
✅ **AI-powered insights** for supply chain security  

This system enables **proactive risk management** and **faster decision-making** by providing immediate AI insights into supply chain threats and vendor risks! 🚀
