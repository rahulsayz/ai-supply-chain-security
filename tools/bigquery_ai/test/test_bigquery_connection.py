#!/usr/bin/env python3
"""
Test BigQuery connectivity with the new service account
"""
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

# Load environment variables
load_dotenv('../.env')

def test_bigquery_connection():
    """Test BigQuery connectivity"""
    try:
        print("🔧 Testing BigQuery connectivity...")
        print(f"Project ID: {os.getenv('GCP_PROJECT_ID')}")
        print(f"Service Account: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
        
        # Initialize BigQuery client
        client = bigquery.Client(project=os.getenv('GCP_PROJECT_ID'))
        print("✅ BigQuery client initialized successfully")
        
        # Test basic connectivity by listing datasets
        datasets = list(client.list_datasets())
        print(f"✅ Successfully connected to BigQuery!")
        print(f"📊 Found {len(datasets)} datasets:")
        
        for dataset in datasets[:5]:  # Show first 5 datasets
            print(f"  - {dataset.dataset_id}")
            
        if len(datasets) > 5:
            print(f"  ... and {len(datasets) - 5} more")
            
        return True
        
    except DefaultCredentialsError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bigquery_connection()
    if success:
        print("\n🎉 BigQuery connectivity test PASSED!")
    else:
        print("\n💥 BigQuery connectivity test FAILED!")
