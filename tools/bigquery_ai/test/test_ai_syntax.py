#!/usr/bin/env python3
"""
Test different BigQuery AI function syntaxes
"""
import os
from google.cloud import bigquery

def test_ai_syntax():
    """Test different BigQuery AI function syntaxes"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing Different BigQuery AI Function Syntaxes...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: Try using ai.generate_text (lowercase)
        print("\n🧪 Test 1: ai.generate_text (lowercase)")
        try:
            query = """
            SELECT ai.generate_text(
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ ai.generate_text query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ ai.generate_text failed: {e}")
        
        # Test 2: Try using the MODEL keyword with a built-in model
        print("\n🧪 Test 2: MODEL keyword with built-in model")
        try:
            query = """
            SELECT AI.GENERATE_TEXT(
                MODEL `ai-sales-agent-452915.supply_chain_ai.gemini_model`,
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ MODEL keyword query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ MODEL keyword failed: {e}")
        
        # Test 3: Try using the built-in Gemini model directly
        print("\n🧪 Test 3: Built-in Gemini model direct usage")
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
        
        # Test 4: Try using the ML functions with correct syntax
        print("\n🧪 Test 4: ML functions with correct syntax")
        try:
            query = """
            SELECT ML.GENERATE_EMBEDDING(
                MODEL `ai-sales-agent-452915.supply_chain_ai.embedding_model`,
                'This is a test threat report'
            ) as embedding
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ ML.GENERATE_EMBEDDING query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ ML.GENERATE_EMBEDDING failed: {e}")
        
        # Test 5: Check if we can use the functions in a different way
        print("\n🧪 Test 5: Alternative function usage")
        try:
            query = """
            SELECT * FROM AI.GENERATE_TABLE(
                'Generate a table with 3 columns: threat_id, severity, description'
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Alternative AI.GENERATE_TABLE query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Alternative AI.GENERATE_TABLE failed: {e}")
        
        print("\n🎯 BigQuery AI Syntax Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_ai_syntax()

