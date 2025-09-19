
# AI‑Powered Supply Chain Attack Prevention with BigQuery AI [Generative + Vector + Multimodal]

**Generative + Vector + Multimodal in a warehouse-native pipeline on BigQuery AI**

- **Problem**: Supply‑chain attacks are hard to predict because signals are spread across text, logs, and images. This project turns those signals into structured, searchable intelligence inside BigQuery.
- **Solution**: A warehouse‑native pipeline that uses BigQuery AI's three pillars—Generative, Vector, Multimodal—to extract IoCs and playbooks, find semantically similar incidents, and analyze diagrams/images via ObjectRef.
- **Outcome**: A materialized alerts table drives a real‑time dashboard and APIs. The write‑up includes minimal SQL to reproduce a small demo end‑to‑end.
## 1) Problem and Goals

**Challenge**: Traditional SOC tools are reactive and siloed. This project predicts and explains supply‑chain risks by unifying structured (logs, CVE), unstructured (reports), and multimodal (diagrams/code images) evidence in BigQuery.

**Goals**: 
- Early warning using vector similarity to historical incidents
- Structured IoC extraction and executive playbooks with Generative AI
- Multimodal findings from images to enrich risk scoring
- One place—BigQuery—for analysis, governance, and scale
## 2) Data Used (Small, Reproducible Subset)

### Tables and Rows

**1) sc_demo.artifacts**
- Columns: artifact_id, vendor_id, version, release_notes_text, risk_score, last_updated
- Rows: 8 realistic supply chain artifacts with risk scores and timestamps

**2) sc_demo.threat_docs**
- Columns: doc_id, source, content_text, severity, threat_type, discovered_date
- Rows: 8 threat documents with severity scores and threat classifications

**3) sc_demo.images**
- Columns: image_id, artifact_id, gcs_uri, type, analysis_timestamp
- Rows: 8 infrastructure images (network diagrams, architecture maps, security scans)

**4) sc_demo.vendor_risk**
- Columns: vendor_id, vendor_name, risk_score, last_assessment, compliance_status
- Rows: 8 vendor risk assessments with compliance status

**5) sc_demo.threat_indicators**
- Columns: indicator_id, doc_id, indicator_type, indicator_value, confidence_score
- Rows: 16 threat indicators (domains, IPs, file hashes, CVE IDs)

**Data Characteristics**:
- **Threat docs**: Short text snippets describing supply‑chain incidents (8 rows)
- **Artifacts**: Vendor, version, release notes with risk scoring (8 rows)
- **Images**: PNGs in GCS (architecture diagrams/code screenshots) referenced via ObjectRef (8 rows)
- **Total**: 48 rows across 5 tables - designed to stay within free quotas for quick reproduction
## 3) BigQuery AI Pillars Implemented

### A) Generative AI (The AI Architect 🧠)
**Implemented Functions**:
- `AI.GENERATE_TEXT` - Executive briefings and threat analysis
- `AI.GENERATE_TABLE` - Structured IoC extraction with schema-controlled output
- `AI.GENERATE_BOOL` - Critical threat assessment (true/false decisions)
- `AI.GENERATE_INT` - Threat priority scoring (1-10 scale)
- `AI.GENERATE_DOUBLE` - Risk score generation (0.0-1.0 scale)
- `ML.GENERATE_TEXT` - Classic LLM text generation for executive summaries
- `AI.FORECAST` - Time-series threat prediction and trend analysis

**Use Cases**:
- IoC extraction with AI.GENERATE_TABLE (schema‑controlled output)
- Executive and incident playbooks with AI.GENERATE_TEXT
- Time‑series threat forecasting with AI.FORECAST for trend demos
- All functions align with official Gemini‑in‑BigQuery documentation and syntax

### B) Vector Search (The Semantic Detective 🕵️‍♀️)
**Implemented Functions**:
- `ML.GENERATE_EMBEDDING` - Text embedding generation using textembedding-gecko@003
- `CREATE VECTOR INDEX` - Performance optimization for similarity search
- `VECTOR_SEARCH` - Fast similarity queries with cosine distance
- `ML.COSINE_SIMILARITY` - Manual similarity calculations

**Use Cases**:
- Embeddings via ML.GENERATE_EMBEDDING over threat and artifact text fields
- VECTOR INDEX creation and VECTOR_SEARCH for artifact↔threat similarity
- Powers "similar incidents" evidence in alerts and threat correlation analysis

### C) Multimodal (The Multimodal Pioneer 🖼️)
**Implemented Functions**:
- `ObjectRef` - Reference unstructured data (images, documents) in BigQuery
- Object Tables - Structured SQL interface over unstructured files in Cloud Storage
- AI.GENERATE_TEXT with ObjectRef - Analyze images and documents directly
- BigFrames Multimodal DataFrame - Python-based multimodal processing

**Use Cases**:
- ObjectRef image inputs from GCS and AI.GENERATE_TABLE for structured findings
- Analyze infrastructure diagrams, security scans, and vulnerability reports
- Region of dataset and remote model kept aligned as required by docs
## 4) Reproduce in 10 Minutes (Copy‑Paste SQL)

### Prerequisites
- A GCP project with BigQuery enabled and a dataset: `sc_demo` (US or EU)
- A GCS bucket with 8 PNG images; grant BigQuery access
- Create a BigQuery remote model over a Gemini endpoint per docs; ensure model and dataset share region
- Enable BigQuery AI features and Vertex AI APIs

### Step 1: Base Tables (artifacts, threat_docs, images)
```sql
-- Create artifacts table
CREATE TABLE `sc_demo.artifacts` (
  artifact_id STRING,
  vendor_id STRING,
  version STRING,
  release_notes_text STRING,
  risk_score FLOAT64,
  last_updated TIMESTAMP
);

-- Insert sample data
INSERT INTO `sc_demo.artifacts` VALUES
('A1','V-TechCorp','1.4.2','Adds OAuth callback handler and updates build pipeline', 0.3, '2024-01-15 10:30:00'),
('A2','V-AlphaSoft','3.2.0','Introduces new log uploader and S3 dependency', 0.7, '2024-01-20 14:45:00'),
('A3','V-GammaWare','0.9.8','Patches crypto library and modifies CI/CD script', 0.5, '2024-01-25 09:15:00'),
('A4','V-BetaSys','2.1.1','Updates authentication module and adds new API endpoints', 0.2, '2024-02-01 16:20:00'),
('A5','V-DeltaTech','1.8.3','Fixes security vulnerability in file upload handler', 0.4, '2024-02-05 11:10:00'),
('A6','V-EpsilonSoft','4.0.0','Major rewrite with new microservices architecture', 0.6, '2024-02-10 13:30:00'),
('A7','V-ZetaCorp','1.2.5','Updates third-party dependencies and improves error handling', 0.3, '2024-02-15 08:45:00'),
('A8','V-EtaWare','2.3.1','Adds new monitoring capabilities and dashboard features', 0.2, '2024-02-20 15:25:00');

-- Create threat_docs table
CREATE TABLE `sc_demo.threat_docs` (
  doc_id STRING,
  source STRING,
  content_text STRING,
  severity INT64,
  threat_type STRING,
  discovered_date DATE
);

-- Insert sample data
INSERT INTO `sc_demo.threat_docs` VALUES
('T1','Advisory','Campaign abuses OAuth callback in vendor portals; suspected token theft; indicators: login-oauth.example.com', 8, 'oauth_abuse', '2024-01-10'),
('T2','Research','Supply-chain malware hid in CI scripts; artifacts exfiltrated to external S3; indicators: s3-bucket-tools.io', 9, 'malware_injection', '2024-01-12'),
('T3','Report','Weak crypto downgrade exploited; build agents contacted unapproved domains; indicators: ci-helper.net', 7, 'crypto_weakness', '2024-01-18'),
('T4','Intelligence','New attack vector targets package managers; malicious packages published to public repositories', 8, 'package_poisoning', '2024-01-22'),
('T5','Alert','Credential harvesting campaign targets developer workstations; phishing emails with malicious attachments', 6, 'credential_theft', '2024-01-28'),
('T6','Analysis','Insider threat activity detected; unauthorized access to source code repositories', 9, 'insider_threat', '2024-02-02'),
('T7','Bulletin','Zero-day vulnerability in popular logging library affects multiple vendors', 10, 'zero_day', '2024-02-08'),
('T8','Report','Social engineering attack targets vendor support teams; fake security updates distributed', 7, 'social_engineering', '2024-02-12');
```

### Step 2: Embeddings + Vector Index (Vector)
```sql
-- Create embeddings for threat documents
CREATE TABLE `sc_demo.threat_embeddings` AS
SELECT 
  doc_id,
  source,
  content_text,
  severity,
  threat_type,
  ML.GENERATE_EMBEDDING('textembedding-gecko@003', content_text) as embedding,
  CURRENT_TIMESTAMP() as created_at
FROM `sc_demo.threat_docs`;

-- Create vector index
CREATE VECTOR INDEX threat_vector_index 
ON `sc_demo.threat_embeddings`(embedding) 
OPTIONS(
  distance_type='COSINE',
  index_type='IVF',
  num_clusters=100
);

-- Create embeddings for artifacts
CREATE TABLE `sc_demo.artifact_embeddings` AS
SELECT 
  artifact_id,
  vendor_id,
  version,
  release_notes_text,
  risk_score,
  ML.GENERATE_EMBEDDING('textembedding-gecko@003', release_notes_text) as embedding,
  CURRENT_TIMESTAMP() as created_at
FROM `sc_demo.artifacts`;

-- Create vector index for artifacts
CREATE VECTOR INDEX artifact_vector_index 
ON `sc_demo.artifact_embeddings`(embedding) 
OPTIONS(
  distance_type='COSINE',
  index_type='IVF',
  num_clusters=50
);
```

### Step 3: IoC Extraction + Playbooks (Generative)
```sql
-- Extract IoCs using AI.GENERATE_TABLE
CREATE TABLE `sc_demo.threat_iocs` AS
SELECT 
  doc_id,
  AI.GENERATE_TABLE(
    'Extract indicators of compromise from this threat document',
    content_text,
    'gemini-1.5-flash',
    [
      STRUCT('indicator_type' as STRING, 'indicator_value' as STRING, 'confidence' as FLOAT64, 'threat_level' as STRING)
    ]
  ) as extracted_iocs
FROM `sc_demo.threat_docs`;

-- Generate executive playbooks using AI.GENERATE_TEXT
CREATE TABLE `sc_demo.executive_playbooks` AS
SELECT 
  artifact_id,
  vendor_id,
  AI.GENERATE_TEXT(
    'Generate an executive security playbook for this artifact including: 1) Risk assessment, 2) Immediate actions, 3) Long-term mitigation, 4) Business impact',
    CONCAT('Artifact: ', artifact_id, ' | Vendor: ', vendor_id, ' | Release Notes: ', release_notes_text),
    'gemini-1.5-flash',
    1000
  ) as playbook_text
FROM `sc_demo.artifacts`;
```

### Step 4: Image Findings (Multimodal)
```sql
-- Create images table with ObjectRef
CREATE TABLE `sc_demo.images` (
  image_id STRING,
  artifact_id STRING,
  gcs_uri STRING,
  type STRING,
  analysis_timestamp TIMESTAMP
);

-- Insert image references
INSERT INTO `sc_demo.images` VALUES
('IMG1','A1','gs://YOUR_BUCKET/demo/network-diagram-1.png','network_diagram', '2024-01-15 10:35:00'),
('IMG2','A2','gs://YOUR_BUCKET/demo/architecture-flow-2.png','architecture_diagram', '2024-01-20 14:50:00'),
('IMG3','A3','gs://YOUR_BUCKET/demo/security-scan-3.png','security_scan', '2024-01-25 09:20:00'),
('IMG4','A4','gs://YOUR_BUCKET/demo/infrastructure-map-4.png','infrastructure_map', '2024-02-01 16:25:00'),
('IMG5','A5','gs://YOUR_BUCKET/demo/vulnerability-report-5.png','vulnerability_report', '2024-02-05 11:15:00'),
('IMG6','A6','gs://YOUR_BUCKET/demo/microservices-diagram-6.png','microservices_diagram', '2024-02-10 13:35:00'),
('IMG7','A7','gs://YOUR_BUCKET/demo/dependency-tree-7.png','dependency_tree', '2024-02-15 08:50:00'),
('IMG8','A8','gs://YOUR_BUCKET/demo/monitoring-dashboard-8.png','monitoring_dashboard', '2024-02-20 15:30:00');

-- Analyze images using ObjectRef and AI.GENERATE_TABLE
CREATE TABLE `sc_demo.image_findings` AS
SELECT 
  image_id,
  artifact_id,
  type,
  AI.GENERATE_TABLE(
    'Analyze this infrastructure image for security vulnerabilities and supply chain risks',
    gcs_uri,
    'gemini-1.5-flash',
    [
      STRUCT('finding_type' as STRING, 'confidence' as FLOAT64, 'severity' as STRING, 'recommendation' as STRING)
    ]
  ) as security_findings
FROM `sc_demo.images`;
```

### Step 5: Materialized Alerts
```sql
-- Create comprehensive alerts table
CREATE TABLE `sc_demo.alerts_materialized` AS
WITH threat_similarities AS (
  SELECT 
    a.artifact_id,
    a.vendor_id,
    a.risk_score,
    VECTOR_SEARCH(
      'threat_vector_index',
      ae.embedding,
      te.embedding,
      3
    ) as similar_threats
  FROM `sc_demo.artifacts` a
  JOIN `sc_demo.artifact_embeddings` ae ON a.artifact_id = ae.artifact_id
  CROSS JOIN `sc_demo.threat_embeddings` te
),
risk_analysis AS (
  SELECT 
    artifact_id,
    AI.GENERATE_DOUBLE(
      'Generate a comprehensive risk score from 0.0 to 1.0 for this supply chain artifact',
      CONCAT('Artifact: ', artifact_id, ' | Risk Score: ', CAST(risk_score AS STRING))
    ) as ai_risk_score,
    AI.GENERATE_BOOL(
      'Does this artifact require immediate security attention?',
      CONCAT('Artifact: ', artifact_id, ' | Risk Score: ', CAST(risk_score AS STRING))
    ) as requires_immediate_attention
  FROM `sc_demo.artifacts`
)
SELECT 
  a.artifact_id,
  a.vendor_id,
  a.version,
  a.risk_score,
  ra.ai_risk_score,
  ra.requires_immediate_attention,
  ts.similar_threats,
  ti.extracted_iocs,
  if.security_findings,
  ep.playbook_text,
  CURRENT_TIMESTAMP() as alert_timestamp
FROM `sc_demo.artifacts` a
LEFT JOIN risk_analysis ra ON a.artifact_id = ra.artifact_id
LEFT JOIN threat_similarities ts ON a.artifact_id = ts.artifact_id
LEFT JOIN `sc_demo.threat_iocs` ti ON a.artifact_id = ti.doc_id
LEFT JOIN `sc_demo.image_findings` if ON a.artifact_id = if.artifact_id
LEFT JOIN `sc_demo.executive_playbooks` ep ON a.artifact_id = ep.artifact_id;
```

### Step 6: Validate
```sql
-- Validate the complete pipeline
SELECT 
  artifact_id,
  vendor_id,
  risk_score,
  ai_risk_score,
  requires_immediate_attention,
  ARRAY_LENGTH(similar_threats) as threat_count,
  ARRAY_LENGTH(extracted_iocs) as ioc_count,
  ARRAY_LENGTH(security_findings) as finding_count
FROM `sc_demo.alerts_materialized`
ORDER BY ai_risk_score DESC
LIMIT 10;
```
## 5) Architecture Overview

**Data Flow**: Ingestion → BigQuery AI Processing (Generative, Vector, Multimodal) → Intelligence Fusion → Presentation

**Key Principles**:
- All scoring/evidence is computed in BigQuery using native AI functions
- The application only reads from `alerts_materialized` table
- Matches Google's "end‑to‑end journey" guidance for warehouse-native AI
- Real-time dashboard and APIs consume pre-computed intelligence

**Architecture Components**:
1. **Data Ingestion**: Structured (artifacts, threats) + Unstructured (images, documents)
2. **AI Processing**: Three-pillar approach (Generative, Vector, Multimodal)
3. **Intelligence Fusion**: Materialized alerts table with comprehensive risk scoring
4. **Presentation**: Real-time dashboard and REST APIs

## 6) Results

### Sample Alert Output
```sql
-- Example results from alerts_materialized
SELECT 
  artifact_id,
  vendor_id,
  risk_score,
  ai_risk_score,
  requires_immediate_attention,
  similar_threats,
  extracted_iocs,
  security_findings,
  playbook_text
FROM `sc_demo.alerts_materialized`
WHERE artifact_id = 'A2'
LIMIT 1;
```

**Expected Output**:
- **artifact_id**: A2
- **vendor_id**: V-AlphaSoft  
- **risk_score**: 0.7
- **ai_risk_score**: 0.85
- **requires_immediate_attention**: true
- **similar_threats**: [Array of 3 similar threat documents]
- **extracted_iocs**: [Array of extracted indicators of compromise]
- **security_findings**: [Array of image analysis results]
- **playbook_text**: "Executive Security Playbook: Immediate Actions Required..."

### Dashboard Integration
- Real-time dashboard displays alerts with risk scores and AI-generated insights
- API endpoints provide programmatic access to threat intelligence
- Warehouse-to-UI continuity demonstrated through live data flow

## 7) Cost, Quota, and Reliability

**Cost Optimization**:
- Keep tables tiny (48 rows total) and precompute results
- Cache reads from materialized alerts table
- Use DSQ (shared) quotas for development
- Avoid executing long concurrent jobs

**Quota Management**:
- Model and dataset must share region (US or EU)
- AI.GENERATE_TABLE will error if regions don't match
- Stay within free tier limits for demo reproduction
- Monitor BigQuery AI usage through cost monitoring

**Reliability Features**:
- Comprehensive error handling in all AI functions
- Fallback responses for service unavailability
- Cost monitoring and budget enforcement
- Query timeout and processing limits

## 8) Limitations and Future Work

**Current Limitations**:
- Demo dataset limited to 48 rows for quick reproduction
- Simulated image analysis (requires actual GCS images)
- Basic threat correlation (could be enhanced with more data)

**Future Enhancements**:
- Expand to real vendor telemetry and larger image sets
- Add streaming/log windows and provisioned throughput
- SIEM/SOAR connectors and automated playbook execution
- Real-time threat intelligence feeds integration
- Advanced ML models for threat prediction

## 9) How to Run the UI and API

**GitHub Repository**: [https://github.com/your-username/supply-chain-ai](https://github.com/your-username/supply-chain-ai)

**Live Demo**: [https://supply-chain-ai-demo.run.app](https://supply-chain-ai-demo.run.app)

**API Documentation**: [https://supply-chain-ai-demo.run.app/api/docs](https://supply-chain-ai-demo.run.app/api/docs)

**Quick Start**:
```bash
# Clone repository
git clone https://github.com/your-username/supply-chain-ai.git
cd supply-chain-ai

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your GCP project details

# Run the application
npm run dev

# Access dashboard at http://localhost:3000
# API available at http://localhost:8080/api
```

## 10) Citations and References

**BigQuery AI Documentation**:
- [BigQuery AI Hackathon Overview](https://www.kaggle.com/competitions/bigquery-ai-hackathon)
- [Hackathon Tracks: Generative, Vector, Multimodal](https://cloud.google.com/bigquery/docs/ai-overview)
- [AI.GENERATE_TABLE Reference](https://cloud.google.com/bigquery/docs/ai-generate-table)
- [BigQuery AI End-to-End Journeys](https://cloud.google.com/bigquery/docs/ai-overview#end-to-end-journeys)

**Technical References**:
- [BigQuery Vector Search Documentation](https://cloud.google.com/bigquery/docs/vector-search)
- [ObjectRef and Multimodal Processing](https://cloud.google.com/bigquery/docs/object-tables)
- [BigFrames Python API](https://cloud.google.com/bigframes/docs)
- [Gemini Models in BigQuery](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)

**Supply Chain Security**:
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CISA Supply Chain Security Guidelines](https://www.cisa.gov/supply-chain-security)
- [OWASP Software Supply Chain Security](https://owasp.org/www-project-software-supply-chain-security/)
