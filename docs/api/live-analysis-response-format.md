# 🔍 Live Analysis API Response Format - Complete Reference

## 📡 **API Endpoint**
```
POST /api/bigquery-ai/live-analysis
Content-Type: text/event-stream
```

## 🚀 **Real-Time Streaming Response Format**

The Live Analysis API sends **Server-Sent Events (SSE)** with multiple data chunks. Here's the **exact format** your UI should expect:

---

## **1. Initial Status Message**
```json
data: {
  "type": "status",
  "message": "Starting Live BigQuery AI Analysis...",
  "timestamp": "2025-08-30T03:01:10.918Z",
  "step": "initialization"
}
```

---

## **2. Step Start Messages (6 total)**
```json
data: {
  "type": "step_start",
  "step": "data_preparation",
  "message": "Preparing data for AI analysis...",
  "timestamp": "2025-08-30T03:01:10.918Z",
  "stepNumber": 1,
  "totalSteps": 6
}

data: {
  "type": "step_start",
  "step": "ai_processing",
  "message": "Running BigQuery AI models...",
  "timestamp": "2025-08-30T03:01:11.918Z",
  "stepNumber": 2,
  "totalSteps": 6
}

data: {
  "type": "step_start",
  "step": "vector_search",
  "message": "Performing vector similarity search...",
  "timestamp": "2025-08-30T03:01:13.918Z",
  "stepNumber": 3,
  "totalSteps": 6
}

data: {
  "type": "step_start",
  "step": "pattern_analysis",
  "message": "Analyzing threat patterns...",
  "timestamp": "2025-08-30T03:01:15.418Z",
  "stepNumber": 4,
  "totalSteps": 6
}

data: {
  "type": "step_start",
  "step": "risk_assessment",
  "message": "Generating risk assessment...",
  "timestamp": "2025-08-30T03:01:16.418Z",
  "stepNumber": 5,
  "totalSteps": 6
}

data: {
  "type": "step_start",
  "step": "insights_generation",
  "message": "Generating AI insights...",
  "timestamp": "2025-08-30T03:01:17.918Z",
  "stepNumber": 6,
  "totalSteps": 6
}
```

---

## **3. Step Completion Messages (6 total) - WITH COSTS & PROGRESS**
```json
data: {
  "type": "step_complete",
  "step": "data_preparation",
  "message": "Preparing data for AI analysis... - Completed",
  "timestamp": "2025-08-30T03:01:11.918Z",
  "stepNumber": 1,
  "totalSteps": 6,
  "cost_usd": 0.008,
  "progress": 16.67
}

data: {
  "type": "step_complete",
  "step": "ai_processing",
  "message": "Running BigQuery AI models... - Completed",
  "timestamp": "2025-08-30T03:01:13.918Z",
  "stepNumber": 2,
  "totalSteps": 6,
  "cost_usd": 0.016,
  "progress": 33.33
}

data: {
  "type": "step_complete",
  "step": "vector_search",
  "message": "Performing vector similarity search... - Completed",
  "timestamp": "2025-08-30T03:01:15.418Z",
  "stepNumber": 3,
  "totalSteps": 6,
  "cost_usd": 0.024,
  "progress": 50.00
}

data: {
  "type": "step_complete",
  "step": "pattern_analysis",
  "message": "Analyzing threat patterns... - Completed",
  "timestamp": "2025-08-30T03:01:16.418Z",
  "stepNumber": 4,
  "totalSteps": 6,
  "cost_usd": 0.032,
  "progress": 66.67
}

data: {
  "type": "step_complete",
  "step": "risk_assessment",
  "message": "Generating risk assessment... - Completed",
  "timestamp": "2025-08-30T03:01:17.918Z",
  "stepNumber": 5,
  "totalSteps": 6,
  "cost_usd": 0.040,
  "progress": 83.33
}

data: {
  "type": "step_complete",
  "step": "insights_generation",
  "message": "Generating AI insights... - Completed",
  "timestamp": "2025-08-30T03:01:18.918Z",
  "stepNumber": 6,
  "totalSteps": 6,
  "cost_usd": 0.048,
  "progress": 100.00
}
```

---

## **4. Final Analysis Results - WITH 92% CONFIDENCE & $0.064 COST**
```json
data: {
  "type": "analysis_complete",
  "message": "Live BigQuery AI Analysis completed successfully",
  "timestamp": "2025-08-30T03:01:18.918Z",
  "results": {
    "vendorId": "V001",
    "threatId": "RPT001",
    "analysisType": "comprehensive",
    "queryText": "Analyze supply chain security",
    "assetIds": ["A001", "A002"],
    "ai_insights": {
      "threat_patterns": [
        {
          "pattern": "supply_chain_compromise",
          "confidence": 0.94,
          "risk_level": "high"
        },
        {
          "pattern": "vendor_vulnerability",
          "confidence": 0.87,
          "risk_level": "medium"
        },
        {
          "pattern": "data_exfiltration",
          "confidence": 0.82,
          "risk_level": "medium"
        }
      ],
      "risk_assessment": {
        "overall_risk_score": 7.8,
        "risk_level": "high",
        "confidence": 0.92,
        "factors": [
          "vendor_security_posture",
          "threat_intelligence",
          "historical_incidents",
          "supply_chain_exposure"
        ]
      },
      "recommendations": [
        "Implement enhanced vendor security assessments",
        "Deploy real-time threat monitoring",
        "Establish incident response protocols",
        "Conduct regular security audits"
      ]
    },
    "processing_metadata": {
      "total_steps": 6,
      "processing_time_ms": 8000,
      "cost_usd": 0.048,
      "cost_breakdown": {
        "ai_processing": 0.016,
        "vector_search": 0.012,
        "pattern_analysis": 0.008,
        "risk_assessment": 0.012,
        "data_processing": 0.008,
        "insights_generation": 0.008
      },
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

---

## **5. End Marker**
```json
data: {
  "type": "end"
}
```

---

## 🎯 **Key Values Your UI Should Display**

### **AI Confidence: 92%**
- **Source**: `results.ai_insights.risk_assessment.confidence`
- **Value**: `0.92` (92%)
- **UI Display**: Should show **92%** not **0.8%**

### **Total Cost: $0.048**
- **Source**: `results.processing_metadata.cost_usd`
- **Value**: `0.048` ($0.048)
- **UI Display**: Should show **$0.048** not **$0.006**

### **Progress Updates**
- **Source**: `progress` field in step_complete messages
- **Values**: 16.67%, 33.33%, 50.00%, 66.67%, 83.33%, 100.00%
- **UI Display**: Should show real-time progress bar

### **High Confidence Scores**
- **Supply Chain Compromise**: **94%** (`0.94`)
- **Vendor Vulnerability**: **87%** (`0.87`)
- **Data Exfiltration**: **82%** (`0.82`)
- **Overall Risk Assessment**: **92%** (`0.92`)

---

## 🔧 **UI Implementation Checklist**

### **Progress Bar**
```javascript
// Update progress bar with each step_complete message
if (data.type === 'step_complete') {
  updateProgressBar(data.progress); // 0-100%
  updateCostDisplay(data.cost_usd); // Real-time cost
}
```

### **Confidence Display**
```javascript
// Extract confidence from final results
if (data.type === 'analysis_complete') {
  const confidence = data.results.ai_insights.risk_assessment.confidence;
  const confidencePercent = Math.round(confidence * 100);
  displayConfidence(confidencePercent); // Should show 92%
}
```

### **Cost Display**
```javascript
// Extract total cost from final results
if (data.type === 'analysis_complete') {
  const totalCost = data.results.processing_metadata.cost_usd;
  displayTotalCost(totalCost); // Should show $0.048
}
```

---

## 🚨 **Common UI Issues to Check**

1. **Confidence Display**: Ensure you're multiplying by 100 (`confidence * 100`)
2. **Cost Formatting**: Ensure proper decimal formatting (`$0.048` not `$0.048000`)
3. **Progress Updates**: Listen for `step_complete` messages, not just `step_start`
4. **Final Results**: Wait for `analysis_complete` message for final data

Your UI should now correctly display:
- ✅ **AI Confidence: 92%** (not 0.8%)
- ✅ **Total Cost: $0.048** (not $0.006)
- ✅ **Real-time Progress: 0% → 100%**
- ✅ **High-quality threat detection scores**
