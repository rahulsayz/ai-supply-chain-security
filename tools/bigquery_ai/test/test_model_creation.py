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
        
        # Test 1: AI.GENERATE_TEXT with correct syntax
        print("\n🧪 Test 1: AI.GENERATE_TEXT (correct syntax)")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE_TEXT(
              MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
              STRUCT('Generate a brief security summary about cybersecurity threats' AS prompt)
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TEXT failed: {e}")
        
        # Test 2: AI.GENERATE_TEXT with model (redundant but example)
        print("\n🧪 Test 2: AI.GENERATE_TEXT with model")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE_TEXT(
              MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
              STRUCT('Generate a brief security summary about cybersecurity threats' AS prompt)
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TEXT with model query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TEXT with model failed: {e}")
        
        # Test 3: ML.GENERATE_EMBEDDING with correct syntax
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
        
        # Test 4: AI.GENERATE_TABLE with correct syntax
        print("\n🧪 Test 4: AI.GENERATE_TABLE (correct syntax)")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE_TABLE(
              MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
              STRUCT('Generate a table with 3 columns: threat_id INT64, severity STRING, description STRING' AS output_schema)
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI.GENERATE_TABLE query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI.GENERATE_TABLE failed: {e}")
        
        # Test 5: Alternative function usage (same as test 1 here)
        print("\n🧪 Test 5: Alternative function usage")
        try:
            query = """
            SELECT *
            FROM AI.GENERATE_TEXT(
              MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
              STRUCT('Generate a brief security summary about cybersecurity threats' AS prompt)
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Alternative AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Alternative AI.GENERATE_TEXT failed: {e}")
        
        print("\n🎯 BigQuery AI Correct Syntax Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_correct_syntax()
