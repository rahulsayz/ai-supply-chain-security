#!/bin/bash

# 58xxx CVE Dataset Integration Setup Script
# This script integrates the 58xxx CVE dataset with BigQuery

echo "🚀 Setting up 58xxx CVE Dataset Integration..."
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "integrate_58xxx_cve.py" ]; then
    echo "❌ Please run this script from the tools/bigquery_ai directory"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Python virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking required packages..."
python -c "import google.cloud.bigquery" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ google-cloud-bigquery package not found. Installing..."
    pip install google-cloud-bigquery python-dotenv
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "📝 Please edit .env file with your GCP credentials before continuing"
        echo "   Required: GCP_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS"
        read -p "Press Enter after updating .env file..."
    else
        echo "❌ env.example not found. Please create .env file manually"
        exit 1
    fi
fi

# Check if 58xxx folder exists
if [ ! -d "../../58xxx" ]; then
    echo "❌ 58xxx folder not found in project root"
    exit 1
fi

echo "✅ Environment setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Ensure your .env file has correct GCP credentials"
echo "2. Run: python integrate_58xxx_cve.py"
echo ""
echo "📁 The script will:"
echo "   - Process all CVE JSON files from 58xxx folder"
echo "   - Upload them to BigQuery cve_data dataset"
echo "   - Create enhanced analysis views"
echo "   - Integrate with your existing BigQuery AI endpoints"
echo ""

read -p "Ready to proceed? Press Enter to continue..."

# Run the integration
echo "🚀 Running CVE integration..."
python integrate_58xxx_cve.py

echo ""
echo "🎉 Integration complete! Check the output above for results."
echo ""
echo "🔍 Your existing BigQuery AI endpoints now have access to:"
echo "   - Real CVE data from the 58xxx dataset"
echo "   - Enhanced vulnerability analysis"
echo "   - Vendor risk assessments"
echo "   - Comprehensive threat intelligence"
