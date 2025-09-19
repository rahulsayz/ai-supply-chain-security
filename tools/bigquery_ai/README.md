# BigQuery AI Processing Layer

This directory contains the Python-based BigQuery AI processing component that transforms your supply chain security API from a demo into a genuinely innovative warehouse-native AI solution.

## 🎯 Overview

The BigQuery AI processing layer implements **three distinct AI approaches** using Google's warehouse-native AI capabilities:

1. **Generative AI Approach** - Using AI.GENERATE functions for threat analysis
2. **Vector Search Approach** - Using ML.GENERATE_EMBEDDING for similarity analysis  
3. **Multimodal Approach** - Using ObjectRef for infrastructure analysis

## 🏗️ Architecture

```
tools/bigquery_ai/
├── config.py              # Configuration and environment management
├── cost_monitor.py        # Cost tracking and budget controls
├── ai_processor.py        # Core AI processing functions
├── vector_processor.py    # Vector search and similarity analysis
├── multimodal_processor.py # Infrastructure and multimodal analysis
├── data_export.py         # JSON export for Fastify API
├── main.py               # CLI interface and main execution
├── requirements.txt      # Python dependencies
├── env.example          # Environment configuration template
└── README.md            # This documentation
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Navigate to the BigQuery AI directory
cd tools/bigquery_ai

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your GCP credentials
nano .env
```

### 2. GCP Configuration

Set these environment variables in your `.env` file:

```bash
# Required
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# Optional (with defaults)
DAILY_BUDGET_LIMIT_USD=5.0
MAX_QUERY_COST_USD=1.0
MAX_PROCESSING_MB=100
QUERY_TIMEOUT_SECONDS=30
```

### 3. Service Account Setup

1. Create a service account in your GCP project
2. Grant BigQuery Admin and AI Platform Developer roles
3. Download the JSON key file as `service-account.json`
4. Place it in the `tools/bigquery_ai/` directory

### 4. Initial Setup

```bash
# Setup BigQuery AI environment and demo tables
python main.py setup

# Verify setup
python main.py status
```

## 🤖 AI Functions Implemented

### Generative AI Approach

- **AI.GENERATE_TABLE** - Extract structured threat indicators from unstructured reports
- **AI.GENERATE_TEXT** - Create executive security briefings
- **AI.GENERATE_DOUBLE** - Quantitative risk scoring
- **AI.FORECAST** - Threat prediction analysis

### Vector Search Approach

- **ML.GENERATE_EMBEDDING** - Generate threat pattern embeddings
- **Vector Similarity Search** - Find similar threats using cosine similarity
- **Pattern Analysis** - Analyze threat patterns using vector clustering
- **Correlation Analysis** - Find correlated threats based on embeddings

### Multimodal Approach

- **Infrastructure Analysis** - Analyze network diagrams and physical assets
- **Cyber-Physical Correlation** - Correlate cyber threats with physical infrastructure
- **Geographic Risk Analysis** - Assess supply chain risks by location
- **Network Topology Analysis** - Security analysis of network components

## 💰 Cost Management

### Budget Controls

- **Daily Spending Limit**: $5 USD maximum (configurable)
- **Per-Query Limit**: $1 USD maximum (configurable)
- **Processing Limits**: 100MB maximum per query
- **Timeout Protection**: 30-second query timeout

### Cost Monitoring

```bash
# View current costs
python main.py costs

# Reset daily costs (for testing)
python main.py reset-costs
```

### Cost Estimation

All queries are estimated using BigQuery's dry-run feature before execution to ensure budget compliance.

## 📊 Demo Data

The system automatically creates realistic demo data:

### Threat Reports
- **RPT001**: TechCorp supply chain compromise
- **RPT002**: DataSystems unauthorized access
- **RPT003**: CloudVendor infrastructure compromise

### Infrastructure Objects
- **INF001**: Data center facility (San Francisco)
- **INF002**: Network hub (Chicago)

## 🔧 CLI Commands

### Setup and Status

```bash
# Setup environment
python main.py setup

# Check system status
python main.py status

# View costs
python main.py costs
```

### AI Analysis

```bash
# Analyze specific threat
python main.py analyze-threat --report-id RPT001

# Analyze vendor infrastructure
python main.py analyze-vendor --vendor-id V001

# Perform vector similarity search
python main.py vector-search --report-id RPT001
```

### Data Export

```bash
# Export all AI-enhanced data
python main.py export-data

# Run complete demo pipeline
python main.py demo
```

## 🔌 Fastify API Integration

The BigQuery AI service integrates seamlessly with your existing Fastify backend:

### New API Endpoints

- `GET /api/bigquery-ai/status` - Service status and cost information
- `POST /api/bigquery-ai/analyze-threat` - AI threat analysis
- `POST /api/bigquery-ai/analyze-vendor` - Multimodal vendor analysis
- `POST /api/bigquery-ai/vector-search` - Vector similarity search
- `POST /api/bigquery-ai/export-data` - Export AI-enhanced data
- `POST /api/bigquery-ai/demo` - Run complete AI pipeline
- `GET /api/bigquery-ai/costs` - Cost monitoring
- `POST /api/bigquery-ai/reset-costs` - Reset cost tracking
- `POST /api/bigquery-ai/setup` - Environment setup

### Dual-Mode Architecture

Your API maintains the existing dual-mode architecture:

1. **Static Demo Mode** - Serves precomputed JSON data (existing functionality)
2. **Live AI Mode** - Real-time BigQuery AI processing (new functionality)

Toggle between modes using the `ENABLE_LIVE_MODE` environment variable.

## 🧪 Testing

### Unit Testing

```bash
# Run Python tests (if implemented)
python -m pytest tests/

# Run Fastify API tests
npm test
```

### Integration Testing

```bash
# Test BigQuery AI integration
python main.py demo

# Test API endpoints
curl -X POST http://localhost:8080/api/bigquery-ai/analyze-threat \
  -H "Content-Type: application/json" \
  -d '{"reportId": "RPT001"}'
```

### Cost Validation

```bash
# Verify costs stay under budget
python main.py costs

# Check that queries respect limits
python main.py analyze-threat --report-id RPT001
```

## 🚨 Error Handling

### Graceful Degradation

- **Service Unavailable**: Falls back to static data if BigQuery AI is down
- **Budget Exceeded**: Queries are rejected before execution
- **Timeout Protection**: Queries are killed after 30 seconds
- **Cost Estimation**: Dry-run validation prevents budget overruns

### Error Responses

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "Detailed error description"
  },
  "metadata": {
    "timestamp": "2024-01-15T10:00:00Z",
    "requestId": "req-123"
  }
}
```

## 🔒 Security Features

### Authentication

- Service account authentication for GCP access
- No hardcoded credentials in code
- Environment variable configuration

### Data Protection

- Cost limits prevent runaway spending
- Processing limits prevent resource exhaustion
- Timeout protection prevents hanging queries

### Access Control

- BigQuery dataset isolation
- Service account principle of least privilege
- No sensitive data in logs

## 📈 Performance Optimization

### Query Optimization

- **LIMIT clauses** for demo data control
- **Maximum bytes billed** for cost control
- **Query timeouts** for responsiveness
- **Batch processing** for efficiency

### Caching Strategy

- **In-memory caching** for frequently accessed data
- **Cost tracking** to avoid duplicate expensive queries
- **Result caching** for repeated operations

## 🚀 Deployment

### Local Development

```bash
# Start Fastify API with BigQuery AI integration
npm run dev

# In another terminal, setup BigQuery AI
cd tools/bigquery_ai
python main.py setup
```

### Production Deployment

1. **Environment Variables**: Set production GCP credentials
2. **Service Account**: Use production service account with minimal permissions
3. **Cost Limits**: Adjust budget limits for production usage
4. **Monitoring**: Enable BigQuery audit logging

### Docker Integration

The BigQuery AI service can be containerized:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py", "demo"]
```

## 🔍 Monitoring and Debugging

### Logging

- **Rich console output** with progress indicators
- **Structured logging** for production monitoring
- **Cost tracking** with detailed query logs
- **Error logging** with stack traces

### Health Checks

```bash
# Check service health
python main.py status

# Verify BigQuery connectivity
python main.py analyze-threat --report-id RPT001
```

### Cost Monitoring

```bash
# Real-time cost dashboard
python main.py costs

# Cost history and trends
# (stored in cost_log.json)
```

## 🎯 Competition Differentiation

### Technical Innovation

- **Warehouse-Native AI**: Uses BigQuery's built-in AI functions
- **Three AI Approaches**: Generative, Vector, and Multimodal
- **Real Cost Management**: Actual BigQuery cost tracking under $5
- **Production Architecture**: Enterprise-grade error handling

### Demo Impact

- **Toggle Between Modes**: Static demo vs. live AI processing
- **Real-Time Cost Display**: Show actual spending during demos
- **Live AI Processing**: Execute real BigQuery AI queries on demand
- **Multimodal Analysis**: Combine cyber and physical security

### Business Value

- **Cost Consciousness**: Demonstrate budget management
- **Scalability**: Show enterprise-ready architecture
- **Innovation**: Warehouse-native AI beyond typical hackathons
- **Integration**: Seamless Python-Fastify integration

## 🆘 Troubleshooting

### Common Issues

1. **Service Account Not Found**
   ```bash
   # Verify service account file exists
   ls -la service-account.json
   ```

2. **BigQuery Permission Denied**
   ```bash
   # Check service account roles
   # Ensure BigQuery Admin and AI Platform Developer roles
   ```

3. **Python Dependencies Missing**
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

4. **Cost Limits Exceeded**
   ```bash
   # Reset daily costs (for testing)
   python main.py reset-costs
   ```

### Debug Mode

```bash
# Enable verbose logging
export PYTHONPATH=.
python -u main.py analyze-threat --report-id RPT001
```

## 📚 Additional Resources

- [BigQuery AI Functions Documentation](https://cloud.google.com/bigquery/docs/reference/standard-sql/ai-functions)
- [BigQuery ML Documentation](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [BigQuery Cost Management](https://cloud.google.com/bigquery/docs/cost-controls)

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your changes**
4. **Add tests and documentation**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the main project LICENSE file for details.

---

**🎉 Congratulations!** You now have a production-ready BigQuery AI processing layer that transforms your supply chain security API into a genuinely innovative warehouse-native AI solution. This implementation goes far beyond typical hackathon demos and showcases real enterprise-grade AI capabilities with proper cost management and error handling.
