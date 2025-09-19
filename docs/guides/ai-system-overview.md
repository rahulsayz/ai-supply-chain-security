# AI-Powered Supply Chain Attack Prevention System

## 🚀 Overview

This comprehensive system implements cutting-edge AI technologies to prevent, detect, and respond to supply chain security threats. The system integrates three core AI components:

1. **AI Architect** - Generative SQL & AI Functions
2. **Semantic Detective** - Vectorization & Search  
3. **Multimodal Pioneer** - Unstructured Data & ObjectRefs

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Supply Chain Security                    │
│                     AI-Powered System                      │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼──────┐   ┌───────▼──────┐
            │   Node.js    │   │   Python    │
            │   Backend    │   │   AI Core    │
            └──────────────┘   └──────────────┘
                    │                   │
            ┌───────▼──────┐   ┌───────▼──────┐
            │   REST API   │   │ BigQuery AI │
            │   Endpoints  │   │  Functions   │
            └──────────────┘   └──────────────┘
                    │                   │
            ┌───────▼──────┐   ┌───────▼──────┐
            │   Frontend   │   │ Vector DB   │
            │   Dashboard  │   │  & Storage  │
            └──────────────┘   └──────────────┘
```

## 🔧 Core Components

### 1. AI Architect – Generative SQL & AI Functions

**Purpose**: Implements all Google SQL AI functions for comprehensive threat analysis

**Key Features**:
- `AI.GENERATE_TEXT` - Threat summaries and analysis
- `AI.FORECAST` - Time series threat forecasting
- `AI.GENERATE_TABLE` - Structured risk assessments
- `AI.GENERATE_BOOL/INT/DOUBLE` - Quantitative threat metrics
- `ML.GENERATE_TEXT` - Classic LLM text generation

**Example SQL**:
```sql
SELECT
  AI.GENERATE_TEXT('Generate a supply chain threat summary.', threat_description) AS summary,
  AI.FORECAST('forecast_threat_metric', threats, '2025-09-01', 60) AS forecasted_threats,
  ML.GENERATE_TEXT('text-bison@001', 'Explain this supply chain vulnerability', vuln_info) AS vuln_explanation
FROM threat_log;
```

**API Endpoints**:
- `POST /api/bigquery-ai/threat-intelligence` - Generate threat intelligence
- `POST /api/bigquery-ai/forecast-threats` - Forecast threat metrics
- `POST /api/bigquery-ai/risk-assessment` - Generate risk assessments
- `POST /api/bigquery-ai/incident-response` - Create response plans

### 2. Semantic Detective – Vectorization & Search

**Purpose**: Implements semantic search and similarity analysis using vector embeddings

**Key Features**:
- `ML.GENERATE_EMBEDDING` - Generate text embeddings
- `CREATE VECTOR INDEX` - Create optimized vector indexes
- `VECTOR_SEARCH` - Fast similarity queries
- BigFrames integration for Python-based operations

**Example SQL**:
```sql
-- Generate embeddings
UPDATE threat_table
SET embedding = ML.GENERATE_EMBEDDING('textembedding-gecko@003', description);

-- Create vector index
CREATE VECTOR INDEX threat_vector_index ON threat_table(embedding) 
OPTIONS(distance_type='COSINE');

-- Vector similarity search
SELECT * FROM VECTOR_SEARCH('threat_vector_index', 'embedding', 
  ML.GENERATE_EMBEDDING('textembedding-gecko@003', @query), 5);
```

**Python Integration**:
```python
from bigframes.ml.llm import TextEmbeddingGenerator
embedding_gen = TextEmbeddingGenerator()
emb = embedding_gen.generate(df['threat_text'])
```

**API Endpoints**:
- `POST /api/bigquery-ai/enhanced-vector-search` - Semantic similarity search
- `POST /api/bigquery-ai/generate-embeddings` - Generate embeddings
- `POST /api/bigquery-ai/create-vector-indexes` - Create vector indexes
- `POST /api/bigquery-ai/semantic-clustering` - Perform semantic clustering

### 3. Multimodal Pioneer – Unstructured Data & ObjectRefs

**Purpose**: Handles images, documents, and other unstructured data using AI analysis

**Key Features**:
- ObjectRef for file storage and reference
- AI-powered image/document analysis
- Google Cloud Storage integration
- BigFrames Gemini integration for multimodal processing

**Example SQL**:
```sql
CREATE TABLE supply_chain_assets (
  asset_id STRING,
  evidence_obj ObjectRef,
  comment STRING
);

SELECT
  AI.GENERATE_TEXT('Describe the contents of this document for supply chain review.', evidence_obj) AS document_summary
FROM supply_chain_assets;
```

**Python Integration**:
```python
from bigframes.ml.llm import GeminiTextGenerator
gemini = GeminiTextGenerator()
captioned = gemini.generate(multimodal_df['image'])
```

**API Endpoints**:
- `POST /api/bigquery-ai/analyze-multimodal-asset` - Analyze assets
- `POST /api/bigquery-ai/upload-and-analyze-asset` - Upload and analyze
- `POST /api/bigquery-ai/comprehensive-analysis` - Run all analyses

## 🚀 Getting Started

### Prerequisites

- Google Cloud Platform account with BigQuery enabled
- Python 3.11+
- Node.js 18+
- Google Cloud credentials configured

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd supply-chain-ai-system
```

2. **Install Python dependencies**:
```bash
cd tools/bigquery_ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install Node.js dependencies**:
```bash
cd ../..
npm install
```

4. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your GCP credentials and project details
```

5. **Setup BigQuery AI environment**:
```bash
cd tools/bigquery_ai
python enhanced_ai_processor.py --demo
```

### Running the System

1. **Start the Node.js backend**:
```bash
npm run dev
```

2. **Run comprehensive AI analysis**:
```bash
cd tools/bigquery_ai
python enhanced_ai_processor.py --threat-id THREAT001 --query "supply chain breach" --assets ASSET001 ASSET002
```

3. **Test individual components**:
```bash
# AI SQL analysis
python enhanced_ai_processor.py --threat-id THREAT001

# Vector search
python enhanced_ai_processor.py --query "cybersecurity threat"

# Multimodal analysis
python enhanced_ai_processor.py --assets ASSET001 ASSET002
```

## 📊 API Reference

### Core Analysis Endpoints

#### Comprehensive Analysis
```http
POST /api/bigquery-ai/comprehensive-analysis
Content-Type: application/json

{
  "threatId": "THREAT001",
  "queryText": "supply chain security breach",
  "assetIds": ["ASSET001", "ASSET002"]
}
```

#### Enhanced Vector Search
```http
POST /api/bigquery-ai/enhanced-vector-search
Content-Type: application/json

{
  "queryText": "cybersecurity threat",
  "searchType": "threats",
  "topK": 10
}
```

#### Multimodal Asset Analysis
```http
POST /api/bigquery-ai/analyze-multimodal-asset
Content-Type: application/json

{
  "assetId": "ASSET001"
}
```

### AI Function Endpoints

#### Threat Intelligence
```http
POST /api/bigquery-ai/threat-intelligence
Content-Type: application/json

{
  "threatData": "Detailed threat description..."
}
```

#### Threat Forecasting
```http
POST /api/bigquery-ai/forecast-threats
Content-Type: application/json

{
  "daysAhead": 90
}
```

#### Risk Assessment
```http
POST /api/bigquery-ai/risk-assessment
Content-Type: application/json

{
  "vendorData": "Vendor information and risk factors..."
}
```

## 🔍 Usage Examples

### 1. Threat Analysis Pipeline

```python
from enhanced_ai_processor import EnhancedAIProcessor

processor = EnhancedAIProcessor()

# Run comprehensive analysis
results = processor.run_comprehensive_supply_chain_analysis(
    threat_report_id="THREAT001",
    query_text="supply chain security breach",
    asset_ids=["ASSET001", "ASSET002"]
)

# Display results
processor.display_comprehensive_results(results)
```

### 2. Vector Search Operations

```python
from vector_processor import vector_processor

# Generate embeddings
vector_processor.generate_embeddings_for_threats()

# Create vector indexes
vector_processor.create_vector_indexes()

# Perform semantic search
results = vector_processor.perform_vector_search(
    "cybersecurity threat", 
    "threats", 
    10
)
```

### 3. Multimodal Processing

```python
from multimodal_processor import multimodal_processor

# Upload and analyze asset
upload_result = multimodal_processor.upload_asset_to_gcs(
    "path/to/document.pdf",
    "ASSET001",
    "document"
)

# Analyze with AI
analysis_result = multimodal_processor.analyze_asset_with_ai("ASSET001")
```

## 💰 Cost Management

The system includes comprehensive cost monitoring and budget controls:

- **Real-time cost tracking** for all AI operations
- **Budget limits** and alerts
- **Cost optimization** recommendations
- **Usage analytics** and reporting

### Cost Estimation

| Operation Type | Base Cost | Time Multiplier |
|----------------|-----------|-----------------|
| AI.GENERATE_TEXT | $0.001 | 1.0x - 2.0x |
| AI.FORECAST | $0.002 | 1.0x - 2.0x |
| ML.GENERATE_EMBEDDING | $0.0005 | 1.0x - 3.0x |
| VECTOR_SEARCH | $0.0003 | 1.0x - 3.0x |
| Multimodal Analysis | $0.002 | 1.0x - 2.5x |

## 🔒 Security Features

- **Authentication** via Google Cloud IAM
- **Data encryption** at rest and in transit
- **Audit logging** for all operations
- **Access controls** and role-based permissions
- **Secure credential management**

## 📈 Performance Optimization

- **Vector indexing** for fast similarity search
- **Query caching** and optimization
- **Parallel processing** for multiple analyses
- **Resource monitoring** and scaling
- **Timeout controls** and error handling

## 🧪 Testing

### Run Tests

```bash
# Python tests
cd tools/bigquery_ai
python -m pytest test/

# Node.js tests
npm test
```

### Demo Mode

```bash
cd tools/bigquery_ai
python enhanced_ai_processor.py --demo
```

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify Google Cloud credentials
   - Check service account permissions
   - Ensure BigQuery API is enabled

2. **Vector Index Creation Fails**
   - Verify embedding column exists
   - Check BigQuery version compatibility
   - Ensure sufficient quota

3. **Multimodal Analysis Errors**
   - Verify file upload permissions
   - Check Google Cloud Storage access
   - Ensure file format is supported

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
python enhanced_ai_processor.py --demo
```

## 📚 Additional Resources

- [BigQuery AI Functions Documentation](https://cloud.google.com/bigquery/docs/reference/standard-sql/ai-functions)
- [Vector Search Guide](https://cloud.google.com/bigquery/docs/vector-search)
- [BigFrames Documentation](https://cloud.google.com/bigquery/docs/bigframes)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Contact the development team

---

**Built with ❤️ for Supply Chain Security**
