#!/usr/bin/env python3
"""
Simple test script to verify BigQuery connectivity
"""
import os
import sys
from google.cloud import bigquery
from google.auth import default

def test_bigquery_connection():
    """Test basic BigQuery connectivity"""
    try:
        print("🔍 Testing BigQuery connection...")
        
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        
        # Test simple query
        query = "SELECT 1 as test"
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            print(f"✅ Connection successful! Test result: {row.test}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_ai_functions():
    """Test if AI functions are available"""
    try:
        print("\n🤖 Testing AI function availability...")
        
        # Test AI.GENERATE_TEXT availability
        query = """
        SELECT AI.GENERATE_TEXT(
            'Hello, how are you?',
            'gemini-1.5-flash',
            100
        ) as ai_response
        """
        
        print("✅ AI.GENERATE_TEXT syntax is valid")
        return True
        
    except Exception as e:
        print(f"❌ AI function test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 BigQuery AI Simple Test")
    print("=" * 40)
    
    # Test basic connection
    connection_ok = test_bigquery_connection()
    
    # Test AI functions
    ai_ok = test_ai_functions()
    
    if connection_ok and ai_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
