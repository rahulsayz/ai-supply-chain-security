#!/usr/bin/env python3
"""
Test simple BigQuery AI functions
"""
import os
from google.cloud import bigquery

def test_simple_ai():
    """Test simple BigQuery AI functions"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing Simple BigQuery AI Functions...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: Simple AI.GENERATE_TEXT (without MODEL)
        print("\n🧪 Test 1: AI.GENERATE_TEXT (simple)")
        try:
            query = """
            SELECT AI.GENERATE_TEXT(
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            # Try to estimate cost first
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TEXT failed: {e}")
        
        # Test 2: Check if we can use the built-in Gemini model
        print("\n🧪 Test 2: Built-in Gemini Model")
        try:
            query = """
            SELECT AI.GENERATE_TEXT(
                'gemini-1.5-flash',
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Built-in Gemini model query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Built-in Gemini model failed: {e}")
        
        # Test 3: Check if we can use the built-in embedding model
        print("\n🧪 Test 3: Built-in Embedding Model")
        try:
            query = """
            SELECT ML.GENERATE_EMBEDDING(
                'textembedding-gecko@003',
                'This is a test threat report'
            ) as embedding
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Built-in embedding model query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Built-in embedding model failed: {e}")
        
        # Test 4: Check project location and settings
        print("\n🧪 Test 4: Project Configuration")
        try:
            # Get project info
            project = client.get_project()
            print(f"✅ Project: {project.project_id}")
            print(f"   Name: {project.friendly_name}")
            print(f"   Number: {project.project_number}")
            
            # Get dataset info
            dataset = client.get_dataset('supply_chain_ai')
            print(f"✅ Dataset: {dataset.dataset_id}")
            print(f"   Location: {dataset.location}")
            
        except Exception as e:
            print(f"❌ Project config test failed: {e}")
        
        print("\n🎯 Simple BigQuery AI Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_simple_ai()
