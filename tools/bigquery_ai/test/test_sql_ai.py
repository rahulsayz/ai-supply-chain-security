#!/usr/bin/env python3
"""
Test BigQuery AI functions through SQL DDL
"""
import os
from google.cloud import bigquery

def test_sql_ai():
    """Test BigQuery AI functions through SQL DDL"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing BigQuery AI Functions through SQL DDL...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: Try to create a model using SQL DDL
        print("\n🧪 Test 1: Create Model using SQL DDL")
        try:
            create_model_sql = """
            CREATE MODEL `ai-sales-agent-452915.supply_chain_ai.test_ai_model`
            OPTIONS(model_type='LOGISTIC_REGR')
            AS SELECT 1 as feature, 1 as label
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(create_model_sql, job_config=job_config)
            print(f"✅ Model creation SQL cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Model creation SQL failed: {e}")
        
        # Test 2: Try to use AI functions with a simple query
        print("\n🧪 Test 2: Simple AI Function Query")
        try:
            query = """
            SELECT AI.GENERATE_TEXT(
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Simple AI function query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Simple AI function failed: {e}")
        
        # Test 3: Try to use ML functions with a simple query
        print("\n🧪 Test 3: Simple ML Function Query")
        try:
            query = """
            SELECT ML.GENERATE_EMBEDDING(
                'This is a test threat report'
            ) as embedding
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Simple ML function query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Simple ML function failed: {e}")
        
        # Test 4: Try to use AI functions with a table query
        print("\n🧪 Test 4: AI Function with Table Query")
        try:
            query = """
            SELECT * FROM AI.GENERATE_TABLE(
                'Generate a table with 3 columns: threat_id, severity, description'
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ AI table generation query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ AI table generation failed: {e}")
        
        print("\n🎯 BigQuery AI SQL DDL Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_sql_ai()

