# BigQuery AI Test Suite

This folder contains all test scripts for the BigQuery AI integration components.

## 📁 Test Files

### Core Functionality Tests
- **`test_simple.py`** - Basic BigQuery connectivity and AI function tests
- **`test_bigquery.py`** - Simple BigQuery connection test
- **`test_bigquery_connection.py`** - Enhanced BigQuery connectivity with environment variables
- **`test_config.py`** - Configuration loading and validation tests

### AI Function Tests
- **`test_ai_functions.py`** - Tests for BigQuery AI functions (AI.GENERATE_TEXT, etc.)
- **`test_ai_functions_fixed.py`** - Fixed version of AI function tests
- **`test_ai_syntax.py`** - AI function syntax validation tests
- **`test_correct_syntax.py`** - Corrected AI function syntax tests
- **`test_simple_ai.py`** - Simple AI function availability tests
- **`test_sql_ai.py`** - SQL-based AI function tests

### Cost and Billing Tests
- **`test_billing_api.py`** - Billing service API integration tests
- **`test_cost_monitor.py`** - Cost monitoring functionality tests
- **`test_query_tracking.py`** - Query cost tracking tests
- **`test_realistic_costs.py`** - Realistic cost scenario simulations
- **`test_query_tracking.py`** - Query execution cost tracking

### Model and Infrastructure Tests
- **`test_model_creation.py` - BigQuery ML model creation tests
- **`create_test_model.py`** - Test model creation utilities
- **`minimal_test.py`** - Minimal configuration tests

### Alternative Approaches
- **`test_alternative_approach.py`** - Alternative implementation approaches

## 🚀 Running Tests

### Run All Tests
```bash
cd tools/bigquery_ai/test
python run_all_tests.py
```

### Run Individual Tests
```bash
cd tools/bigquery_ai/test
python test_simple.py
python test_bigquery_connection.py
python test_ai_functions.py
```

### Run Tests with Virtual Environment
```bash
cd tools/bigquery_ai
source venv/bin/activate
cd test
python run_all_tests.py
```

## 🔧 Test Configuration

### Environment Variables
Tests automatically use the correct paths:
- **Service Account**: `../service-account.json`
- **Environment File**: `../.env`
- **Project ID**: `ai-sales-agent-452915`

### Python Path
Tests automatically add the parent directory to Python path to import modules:
- `billing_service`
- `cost_monitor`
- `query_cost_tracker`
- `config`

## 📊 Test Categories

### ✅ **Connectivity Tests**
- BigQuery client initialization
- Service account authentication
- Project access verification

### 🤖 **AI Function Tests**
- AI.GENERATE_TEXT availability
- ML.GENERATE_EMBEDDING functionality
- AI.GENERATE_TABLE operations
- Vector search capabilities

### 💰 **Cost Management Tests**
- Query cost tracking
- Budget enforcement
- Cost alerts and monitoring
- Billing service integration

### 🔍 **Integration Tests**
- End-to-end AI processing
- Multimodal analysis
- Vendor risk assessment
- Threat intelligence extraction

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure you're running from the test directory
2. **Path Issues**: Tests use relative paths from the test folder
3. **Authentication**: Verify service account credentials are valid
4. **Dependencies**: Install requirements with `pip install -r ../requirements.txt`

### Debug Mode
Run tests with verbose output:
```bash
python -v test_simple.py
```

## 📈 Test Results

Tests return structured results:
- **Exit Code 0**: Test passed
- **Exit Code 1**: Test failed
- **Timeout**: 60-second limit per test
- **Output Capture**: Both stdout and stderr are captured

## 🔄 Continuous Integration

The test suite is designed for:
- Local development testing
- CI/CD pipeline integration
- Automated quality assurance
- Hackathon demonstration validation
