#!/bin/bash

# BigQuery AI Integration Setup Script
# This script sets up the BigQuery AI processing layer

set -e

echo "🚀 Setting up BigQuery AI Integration Layer"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is installed
check_python() {
    print_status "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    print_success "pip3 found"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Created .env from env.example"
            print_warning "Please edit .env with your GCP credentials"
        else
            print_error "env.example not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
}

# Check GCP credentials
check_gcp_credentials() {
    print_status "Checking GCP credentials..."
    
    if [ ! -f "service-account.json" ]; then
        print_warning "service-account.json not found"
        print_warning "Please download your GCP service account key and place it in this directory"
        print_warning "You can create one at: https://console.cloud.google.com/iam-admin/serviceaccounts"
    else
        print_success "GCP service account key found"
    fi
    
    if [ -f ".env" ]; then
        if grep -q "your-gcp-project-id" .env; then
            print_warning "Please update GCP_PROJECT_ID in .env with your actual project ID"
        fi
    fi
}

# Validate environment configuration
validate_environment() {
    print_status "Validating environment configuration..."
    
    if [ -f ".env" ]; then
        # Load environment variables
        export $(cat .env | grep -v '^#' | xargs)
        
        if [ -z "$GCP_PROJECT_ID" ] || [ "$GCP_PROJECT_ID" = "your-gcp-project-id" ]; then
            print_warning "GCP_PROJECT_ID not set or using default value"
        fi
        
        if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
            print_warning "GOOGLE_APPLICATION_CREDENTIALS not set"
        fi
    fi
}

# Test BigQuery connectivity
test_bigquery_connectivity() {
    print_status "Testing BigQuery connectivity..."
    
    if [ -f "service-account.json" ] && [ -f ".env" ]; then
        # Load environment variables
        export $(cat .env | grep -v '^#' | xargs)
        
        if [ -n "$GCP_PROJECT_ID" ] && [ "$GCP_PROJECT_ID" != "your-gcp-project-id" ]; then
            print_status "Testing connection to GCP project: $GCP_PROJECT_ID"
            
            # Test with a simple Python command
            if python3 -c "
import os
import json
from google.cloud import bigquery

try:
    client = bigquery.Client(project='$GCP_PROJECT_ID')
    datasets = list(client.list_datasets())
    print(f'Successfully connected to BigQuery. Found {len(datasets)} datasets.')
except Exception as e:
    print(f'Failed to connect to BigQuery: {e}')
    exit(1)
" 2>/dev/null; then
                print_success "BigQuery connectivity test passed"
            else
                print_warning "BigQuery connectivity test failed"
                print_warning "Please check your service account permissions and project ID"
            fi
        else
            print_warning "Skipping BigQuery connectivity test (GCP_PROJECT_ID not configured)"
        fi
    else
        print_warning "Skipping BigQuery connectivity test (credentials not configured)"
    fi
}

# Setup demo environment
setup_demo_environment() {
    print_status "Setting up demo environment..."
    
    if [ -f "main.py" ]; then
        print_status "Running BigQuery AI setup..."
        if python3 main.py setup; then
            print_success "Demo environment setup completed"
        else
            print_warning "Demo environment setup failed"
            print_warning "You may need to configure GCP credentials first"
        fi
    else
        print_error "main.py not found"
        exit 1
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo "🎯 Next Steps:"
    echo "==============="
    echo ""
    
    if [ ! -f "service-account.json" ]; then
        echo "1. 📋 Download your GCP service account key:"
        echo "   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts"
        echo "   - Create a new service account or use existing one"
        echo "   - Grant BigQuery Admin and AI Platform Developer roles"
        echo "   - Download the JSON key file as 'service-account.json'"
        echo ""
    fi
    
    if [ -f ".env" ] && grep -q "your-gcp-project-id" .env; then
        echo "2. 🔧 Update your .env file:"
        echo "   - Set GCP_PROJECT_ID to your actual project ID"
        echo "   - Verify GOOGLE_APPLICATION_CREDENTIALS path"
        echo ""
    fi
    
    echo "3. 🧪 Test the integration:"
    echo "   python3 main.py status"
    echo "   python3 main.py demo"
    echo ""
    
    echo "4. 🔌 Test API integration:"
    echo "   # Start your Fastify API"
    echo "   npm run dev"
    echo ""
    
    echo "5. 📊 Monitor costs:"
    echo "   python3 main.py costs"
    echo ""
    
    echo "🎉 You're ready to use warehouse-native AI in your supply chain security API!"
}

# Main setup function
main() {
    echo ""
    print_status "Starting BigQuery AI integration setup..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Install dependencies
    install_dependencies
    
    # Setup environment
    setup_environment
    
    # Check credentials
    check_gcp_credentials
    
    # Validate environment
    validate_environment
    
    # Test connectivity
    test_bigquery_connectivity
    
    # Setup demo environment
    setup_demo_environment
    
    # Show next steps
    show_next_steps
    
    echo ""
    print_success "BigQuery AI integration setup completed!"
    echo ""
}

# Run main function
main "$@"
