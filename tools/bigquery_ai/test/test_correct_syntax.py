#!/usr/bin/env python3
"""
Test BigQuery AI functions with correct syntax for latest version
"""
import os
from google.cloud import bigquery

def test_correct_syntax():
    """Test BigQuery AI functions with correct syntax"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing BigQuery AI Functions with Correct Syntax...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: AI.GENERATE (correct syntax example)
        print("\n🧪 Test 1: AI.GENERATE (correct syntax)")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE(
              prompt => 'Generate a brief security summary about cybersecurity threats',
              connection_id => 'projects/ai-sales-agent-452915/locations/us/connections/your-vertex-ai-connection'
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE failed: {e}")
        
        # Test 2: AI.GENERATE_TABLE with output schema
        print("\n🧪 Test 2: AI.GENERATE_TABLE (correct syntax)")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE_TABLE(
              MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
              STRUCT(
                'threat_id INT64, severity STRING, description STRING' AS output_schema
              )
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TABLE query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TABLE failed: {e}")
        
        # Test 3: ML.GENERATE_EMBEDDING (example with UNNEST input)
        print("\n🧪 Test 3: ML.GENERATE_EMBEDDING (correct syntax)")
        try:
            query = """
            SELECT *
            FROM ML.GENERATE_EMBEDDING(
              MODEL `ai-sales-agent-452915.supply_chain_ai.embedding_model`,
              TABLE UNNEST([STRUCT('This is a test threat report' AS content)])
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ ML.GENERATE_EMBEDDING query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ ML.GENERATE_EMBEDDING failed: {e}")
        
        # Test 4: Alternative AI.GENERATE usage with additional parameters
        print("\n🧪 Test 4: AI.GENERATE with model_params")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE(
              prompt => 'Generate a brief security summary about cybersecurity threats',
              connection_id => 'projects/ai-sales-agent-452915/locations/us/connections/your-vertex-ai-connection',
              model_params => STRUCT('gemini-1.5-flash' AS model)
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE with model_params query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE with model_params failed: {e}")
        
        print("\n🎯 BigQuery AI Correct Syntax Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_correct_syntax()
