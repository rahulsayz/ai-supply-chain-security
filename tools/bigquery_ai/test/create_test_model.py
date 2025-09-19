#!/usr/bin/env python3
"""
Create a test BigQuery ML model to enable AI functions
"""
import os
from google.cloud import bigquery

def create_test_model():
    """Create a test BigQuery ML model"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Creating test BigQuery ML model...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Create a simple ML model
        dataset_ref = client.dataset('supply_chain_ai')
        model_id = 'test_ml_model'
        
        # Create a simple linear regression model
        model = bigquery.Model(dataset_ref.model(model_id))
        
        # Set model options
        model.model_type = 'LOGISTIC_REGR'
        model.friendly_name = 'Test ML Model'
        model.description = 'A test model to enable BigQuery AI functions'
        
        # Try to create the model
        model = client.create_model(model)
        print(f"✅ Model created successfully: {model.model_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

if __name__ == "__main__":
    success = create_test_model()
    if success:
        print("\n🎉 Test model created successfully!")
    else:
        print("\n💥 Test model creation failed!")
