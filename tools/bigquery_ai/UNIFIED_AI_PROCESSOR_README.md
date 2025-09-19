# 🚀 Unified AI Processor - Supply Chain Security

## 📋 Overview

The **Unified AI Processor** consolidates all AI capabilities from the previous three separate processors into a single, comprehensive system. This eliminates confusion and provides a clean, maintainable codebase for supply chain security analysis.

## 🔄 What Was Consolidated

### Previously Separate Files:
1. **`minimal_ai_processor.py`** - Basic AI operations
2. **`ai_processor.py`** - Infrastructure and cyber-physical analysis  
3. **`ai_sql_processor.py`** - AI SQL functions

### Now Unified Into:
- **`unified_ai_processor.py`** - Single comprehensive processor

## 🏗️ Architecture

```
UnifiedAIProcessor
├── AI SQL Functions (AI.GENERATE_TEXT, AI.FORECAST, etc.)
├── Vector Processing (ML.GENERATE_EMBEDDING, VECTOR_SEARCH)
├── Multimodal Analysis (ObjectRef, image/document/video analysis)
├── Legacy Compatibility (backward compatibility methods)
└── Comprehensive Analysis Pipeline (5-phase analysis)
```

## 🎯 Key Features

### 1. **AI SQL Functions** (from ai_sql_processor.py)
- `AI.GENERATE_TEXT` - Threat summaries and analysis
- `AI.FORECAST` - Threat metric forecasting
- `AI.GENERATE_TABLE` - Risk matrix generation
- `AI.GENERATE_BOOL/INT/DOUBLE` - Structured data generation
- `ML.GENERATE_TEXT` - Classic LLM analysis

### 2. **Vector Processing** (from vector_processor.py)
- `ML.GENERATE_EMBEDDING` - Text embedding generation
- `CREATE VECTOR INDEX` - Fast similarity search indexes
- `VECTOR_SEARCH` - Semantic similarity queries
- `ML.KMEANS` - Semantic clustering

### 3. **Multimodal Analysis** (from multimodal_processor.py)
- `ObjectRef` support for unstructured data
- Image analysis with AI captioning
- Document analysis and extraction
- Video content analysis
- Asset management and tracking

### 4. **Legacy Compatibility**
- Maintains all existing method signatures
- Backward compatibility with existing code
- Gradual migration path

## 🚀 Usage

### Command Line Interface

```bash
# Run comprehensive demo
python unified_ai_processor.py --demo

# Analyze specific threat
python unified_ai_processor.py --threat-id RPT001

# Perform vector search
python unified_ai_processor.py --query "supply chain breach"

# Analyze multiple assets
python unified_ai_processor.py --assets ASSET001 ASSET002

# Full comprehensive analysis
python unified_ai_processor.py --threat-id RPT001 --query "security breach" --assets ASSET001 ASSET002
```

### Programmatic Usage

```python
from unified_ai_processor import unified_ai_processor

# Run comprehensive analysis
results = unified_ai_processor.run_comprehensive_supply_chain_analysis(
    threat_report_id="RPT001",
    query_text="supply chain security",
    asset_ids=["ASSET001", "ASSET002"]
)

# Individual AI SQL functions
threat_summary = unified_ai_processor.generate_threat_summary("threat description")
forecast = unified_ai_processor.forecast_threat_metrics(days_ahead=60)

# Vector operations
embeddings = unified_ai_processor.generate_embeddings_for_threats()
search_results = unified_ai_processor.perform_vector_search("query text")

# Multimodal analysis
asset_analysis = unified_ai_processor.analyze_multimodal_asset("ASSET001")
```

## 🔧 API Endpoints

The unified processor is exposed through the Node.js API with these endpoints:

### Core Analysis
- `POST /api/bigquery-ai/comprehensive-analysis` - Full analysis pipeline
- `POST /api/bigquery-ai/enhanced-vector-search` - Vector similarity search
- `POST /api/bigquery-ai/analyze-multimodal-asset` - Asset analysis

### AI SQL Functions
- `POST /api/bigquery-ai/threat-intelligence` - Threat intelligence generation
- `POST /api/bigquery-ai/forecast-threats` - Threat forecasting
- `POST /api/bigquery-ai/risk-assessment` - Risk assessment
- `POST /api/bigquery-ai/incident-response` - Incident response planning

### Vector Operations
- `POST /api/bigquery-ai/generate-embeddings` - Generate embeddings
- `POST /api/bigquery-ai/create-vector-indexes` - Create vector indexes
- `POST /api/bigquery-ai/semantic-clustering` - Semantic clustering

## 📊 Comprehensive Analysis Pipeline

The unified processor runs a 5-phase analysis:

1. **AI SQL Analysis** - Threat analysis using AI functions
2. **Vector Analysis** - Semantic search and clustering
3. **Multimodal Analysis** - Asset analysis with ObjectRef
4. **Cross-Analysis Correlation** - Pattern identification across phases
5. **Comprehensive Report Generation** - Unified findings and recommendations

## 🔄 Migration Guide

### From minimal_ai_processor.py
```python
# Old way
from minimal_ai_processor import minimal_ai_processor
result = minimal_ai_processor.analyze_threat("RPT001")

# New way
from unified_ai_processor import unified_ai_processor
result = unified_ai_processor.analyze_threat("RPT001")  # Still works!
```

### From ai_processor.py
```python
# Old way
from ai_processor import ai_processor
result = ai_processor.analyze_infrastructure("INFRA001")

# New way
from unified_ai_processor import unified_ai_processor
result = unified_ai_processor.analyze_multimodal_asset("INFRA001")
```

### From ai_sql_processor.py
```python
# Old way
from ai_sql_processor import ai_sql_processor
result = ai_sql_processor.generate_threat_summary("description")

# New way
from unified_ai_processor import unified_ai_processor
result = unified_ai_processor.generate_threat_summary("description")
```

## 🧪 Testing

### Run Demo
```bash
cd tools/bigquery_ai
python unified_ai_processor.py --demo
```

### Test Individual Components
```bash
# Test AI SQL functions
python -c "
from unified_ai_processor import unified_ai_processor
result = unified_ai_processor.generate_threat_summary('Test threat')
print(result)
"

# Test vector operations
python -c "
from unified_ai_processor import unified_ai_processor
result = unified_ai_processor.perform_vector_search('test query')
print(result)
"
```

## 📁 File Structure

```
tools/bigquery_ai/
├── unified_ai_processor.py          # Main unified processor
├── config.py                        # Configuration
├── cost_monitor.py                  # Cost tracking
├── requirements.txt                 # Dependencies
└── UNIFIED_AI_PROCESSOR_README.md  # This file
```

## 🔧 Configuration

The unified processor uses the same configuration as the original processors:

```python
# config.py
config = {
    "gcp_project_id": "your-project-id",
    "gcp_dataset_id": "supply_chain_security",
    "gcp_location": "US",
    "max_query_bytes": 1000000000,  # 1GB
    "daily_budget_limit": 10.0,     # $10/day
    "max_query_cost": 1.0           # $1/query
}
```

## 💰 Cost Management

The unified processor includes comprehensive cost tracking:

- **AI Query Costs** - Estimated based on query type and processing time
- **Vector Query Costs** - Embedding generation and search costs
- **Multimodal Costs** - Asset analysis and ObjectRef processing costs
- **Budget Enforcement** - Automatic cost limits and alerts

## 🚨 Error Handling

The unified processor includes robust error handling:

- **Graceful Degradation** - Continues processing if one component fails
- **Detailed Error Reporting** - Specific error messages for debugging
- **Fallback Mechanisms** - Alternative processing paths when possible
- **Cost Protection** - Automatic query termination on budget limits

## 🔒 Security Features

- **Service Account Authentication** - Secure GCP access
- **Query Validation** - SQL injection prevention
- **Cost Limits** - Prevents runaway queries
- **Audit Logging** - Complete operation tracking

## 📈 Performance Optimization

- **Parallel Processing** - Multiple analysis phases run concurrently
- **Query Optimization** - Efficient BigQuery usage
- **Caching** - Result caching for repeated queries
- **Resource Management** - Automatic cleanup and optimization

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Authentication Issues**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
   ```

3. **BigQuery Permissions**
   - Ensure service account has BigQuery Admin role
   - Check dataset permissions

4. **Cost Exceeded**
   - Review budget configuration
   - Check individual query costs

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from unified_ai_processor import unified_ai_processor
# Run operations with detailed logging
```

## 🔮 Future Enhancements

- **Real-time Streaming** - Live threat analysis
- **Advanced ML Models** - Custom model integration
- **API Rate Limiting** - Enhanced performance controls
- **Multi-cloud Support** - AWS, Azure integration
- **Advanced Analytics** - Predictive threat modeling

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review error logs
3. Test with demo mode
4. Verify configuration settings

## 📝 License

This unified processor is part of the Supply Chain Security System and follows the same licensing terms.

---

**🎯 The Unified AI Processor provides a single, powerful interface for all your supply chain security AI needs!**
