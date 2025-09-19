#!/usr/bin/env python3
"""
Test BigQuery AI function availability
"""
import os
from google.cloud import bigquery
from google.api_core import exceptions

def test_ai_functions():
    """Test if BigQuery AI functions are available"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing BigQuery AI Functions...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: Simple AI.GENERATE_TEXT query
        print("\n🧪 Test 1: AI.GENERATE_TEXT function")
        try:
            query = """
            SELECT AI.GENERATE_TEXT('Generate a brief security summary', 
                                  'gemini-1.5-flash', 
                                  'Generate a 2-sentence summary about cybersecurity') as ai_response
            """
            
            # Try to estimate cost first
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
            # Now try to execute the actual query
            job_config = bigquery.QueryJobConfig()
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                print(f"✅ AI.GENERATE_TEXT working! Response: {row.ai_response}")
                
        except Exception as e:
            print(f"❌ AI.GENERATE_TEXT failed: {e}")
        
        # Test 2: ML.GENERATE_EMBEDDING function
        print("\n🧪 Test 2: ML.GENERATE_EMBEDDING function")
        try:
            query = """
            SELECT ML.GENERATE_EMBEDDING('textembedding-gecko@003', 
                                       'This is a test threat report') as embedding
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ ML.GENERATE_EMBEDDING query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ ML.GENERATE_EMBEDDING failed: {e}")
        
        # Test 3: AI.GENERATE_TABLE function
        print("\n🧪 Test 3: AI.GENERATE_TABLE function")
        try:
            query = """
            SELECT * FROM AI.GENERATE_TABLE(
                'Generate a table with 3 columns: threat_id, severity, description',
                'gemini-1.5-flash',
                'Create a sample threat table'
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TABLE query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TABLE failed: {e}")
        
        print("\n🎯 BigQuery AI Function Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_ai_functions()
