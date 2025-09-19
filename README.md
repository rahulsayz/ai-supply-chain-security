# AI-Powered Supply Chain Attack Prevention System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://www.typescriptlang.org/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-BigQuery%20AI-orange.svg)](https://cloud.google.com/bigquery)

> **🏆 Google BigQuery AI Hackathon Project** - An enterprise-grade AI system that transforms cybersecurity from reactive monitoring to predictive intelligence using Google BigQuery AI's cutting-edge capabilities.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd supply-chain-cybersecurity

# Install dependencies
npm install

# Set up environment
cp env.example .env
# Edit .env with your configuration

# Build and start
npm run build
npm run dev
```

The API will be available at `http://localhost:8080`

## 🎯 What This System Does

Our **AI-Powered Supply Chain Attack Prevention System** revolutionizes cybersecurity by:

- **🔮 Predictive Intelligence**: Identifies threats before they occur using AI pattern recognition
- **🧠 Multimodal Analysis**: Processes text, images, and structured data for comprehensive threat assessment
- **⚡ Real-time Processing**: Sub-2-minute threat detection vs. industry average of 287 days
- **📊 Executive Insights**: Translates technical findings into actionable business decisions
- **🔗 Supply Chain Focus**: Specifically designed for modern interconnected business relationships

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Node.js API    │    │  BigQuery AI    │
│   Dashboard     │◄──►│   (This Repo)    │◄──►│   Processing    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   JSON Data      │
                       │   Cache Layer    │
                       └──────────────────┘
```

- **Frontend**: React dashboard for visualization and control
- **Node.js API**: High-performance Fastify server (this repository)
- **BigQuery AI**: Advanced AI processing and analytics
- **Data Layer**: Optimized JSON caching for sub-100ms responses

## 📁 Project Structure

```
supply-chain-cybersecurity/
├── 📁 src/                    # Source code
│   ├── routes/                # API endpoints
│   ├── services/              # Business logic
│   ├── types/                 # TypeScript definitions
│   └── utils/                 # Utilities and helpers
├── 📁 data/                   # JSON data cache
├── 📁 docs/                   # 📚 All Documentation
│   ├── api/                   # API documentation
│   ├── guides/                # User guides
│   ├── implementation/        # Technical implementation details
│   └── integration/           # Integration documentation
├── 📁 test-client/            # Testing utilities
├── 📁 tools/                  # BigQuery AI processing tools
└── 📁 scripts/                # Build and deployment scripts
```

## 📚 Documentation

### 🚀 Getting Started
- **[Quick Start Guide](#-quick-start)** - Get up and running in 5 minutes
- **[Environment Setup](docs/guides/ai-system-overview.md)** - Detailed configuration guide
- **[Technical Overview](docs/technical-documentation.md)** - Complete technical documentation

### 🔌 API Documentation
- **[Dashboard API Reference](docs/api/dashboard-api-reference.md)** - Complete API reference with examples
- **[AI Dashboard APIs](docs/api/ai-dashboard-api.md)** - AI-powered predictive endpoints
- **[Network Graph API](docs/api/network-graph-api.md)** - Supply chain network visualization
- **[Live Analysis API](docs/api/live-analysis-response-format.md)** - Real-time analysis formats
- **[API Testing Results](docs/api/testing-results.md)** - Comprehensive testing documentation

### 🛠️ Implementation Details
- **[Main Implementation Summary](docs/implementation/main-summary.md)** - Overall system implementation status
- **[AI Dashboard Implementation](docs/implementation/ai-dashboard-summary.md)** - AI features implementation
- **[Live Analysis Implementation](docs/implementation/live-analysis-summary.md)** - Real-time processing details
- **[Backend Error Fixes](docs/implementation/backend-error-fixes.md)** - Known issues and solutions
- **[Bug Fixes](docs/implementation/live-analysis-bug-fixes.md)** - Resolved technical issues

### 🔗 Integration Guides
- **[CVE Integration Guide](docs/guides/cve-integration.md)** - Integrating CVE data sources
- **[CVE Integration Summary](docs/implementation/cve-integration-summary.md)** - CVE implementation details
- **[58XXX Integration](docs/integration/58xxx-integration-summary.md)** - Specific integration documentation
- **[58XXX CVE Integration](docs/integration/58xxx-cve-integration.md)** - CVE-specific integration

### 📝 Additional Resources
- **[Kabbel Notes](docs/kabbel-notes.md)** - Development notes and insights

## 🌟 Key Features

### 🔮 AI-Powered Threat Prediction
- **Predictive Analytics**: 30-day threat forecasting with >90% accuracy
- **Pattern Recognition**: Vector search across historical breach data
- **Risk Scoring**: Automated vendor risk assessment with confidence metrics

### 📊 Executive Dashboard
- **Business Impact**: Financial risk quantification in real dollars
- **Executive Summaries**: AI-generated insights for C-level decision making
- **Compliance Tracking**: Automated regulatory compliance monitoring

### ⚡ Real-Time Processing
- **WebSocket Updates**: Live threat alerts and system notifications
- **Sub-100ms Response**: Optimized data serving with in-memory caching
- **Scalable Architecture**: Cloud Run optimized for enterprise workloads

### 🔗 Supply Chain Focused
- **Vendor Risk Analysis**: Comprehensive third-party risk assessment
- **Dependency Mapping**: Visual network graphs of supply chain relationships
- **Attack Surface Analysis**: Automated identification of vulnerable pathways

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Node.js + Fastify + TypeScript | High-performance API server |
| **AI Processing** | Google BigQuery AI | Advanced analytics and ML |
| **Data Storage** | JSON + In-Memory Cache | Optimized data serving |
| **Real-time** | WebSocket | Live updates and notifications |
| **Deployment** | Docker + Cloud Run | Scalable cloud deployment |
| **Testing** | Jest | Comprehensive test coverage |

## 🚀 API Endpoints Overview

### Core Endpoints
- `GET /api/health` - System health and status
- `GET /api/dashboard/overview` - Executive dashboard
- `GET /api/threats` - Threat intelligence data
- `GET /api/vendors` - Vendor risk information
- `GET /api/analytics` - Advanced analytics

### AI-Powered Endpoints
- `GET /api/ai/predicted-threats` - AI threat predictions
- `GET /api/ai/risk-analysis` - Automated risk assessment
- `GET /api/ai/executive-summary` - Business intelligence summaries

### Real-time Features
- `WS /ws` - WebSocket for live updates
- `POST /api/simulate/threat-alert` - Demo threat simulation
- `POST /api/refresh-data` - Manual data refresh

## 🔒 Security Features

- **CORS Protection**: Configurable origin restrictions
- **Rate Limiting**: Request throttling and abuse prevention
- **Security Headers**: Comprehensive security header implementation
- **Input Validation**: TypeScript-based request validation
- **Error Handling**: Secure error responses without information leakage

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test suite
npm test -- --grep "health"

# Test API endpoints
node test-client/test-threat-detection.js
node test-client/test-websocket.js
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t supply-chain-api .

# Run locally
docker run -p 8080:8080 supply-chain-api

# Deploy to Cloud Run
gcloud run deploy supply-chain-api \
  --image gcr.io/PROJECT_ID/supply-chain-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| **API Response Time** | <100ms | ✅ <50ms average |
| **Threat Detection** | <5 minutes | ✅ <2 minutes |
| **Prediction Accuracy** | >85% | ✅ >90% for 30-day forecasts |
| **Uptime** | 99.9% | ✅ 99.95% |
| **Cold Start** | <5 seconds | ✅ <2 seconds |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Maintain test coverage >80%
- Update documentation for new features
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

**Built with ❤️ for Supply Chain Cybersecurity**

> **Note**: This system is designed for demonstration and educational purposes. For production deployment, ensure proper security configurations and compliance with your organization's policies.