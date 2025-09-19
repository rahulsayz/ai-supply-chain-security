#!/usr/bin/env python3
"""
Test alternative approaches to BigQuery AI functions
"""
import os
from google.cloud import bigquery

def test_alternative_approach():
    """Test alternative approaches to BigQuery AI functions"""
    try:
        # Set environment variables
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'
        os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
        
        print("🔧 Testing Alternative Approaches to BigQuery AI Functions...")
        
        # Initialize BigQuery client
        client = bigquery.Client(project='ai-sales-agent-452915')
        print(f"✅ BigQuery client initialized for project: {client.project}")
        
        # Test 1: Try using the functions as table-valued functions
        print("\n🧪 Test 1: Table-valued function approach")
        try:
            query = """
            SELECT * FROM AI.GENERATE_TEXT(
                'Generate a brief security summary about cybersecurity threats'
            )
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Table-valued AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Table-valued AI.GENERATE_TEXT failed: {e}")
        
        # Test 2: Try using the functions with different syntax
        print("\n🧪 Test 2: Different syntax approach")
        try:
            query = """
            SELECT AI.GENERATE_TEXT(
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports`
            LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Different syntax AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Different syntax AI.GENERATE_TEXT failed: {e}")
        
        # Test 3: Try using the functions with a subquery
        print("\n🧪 Test 3: Subquery approach")
        try:
            query = """
            SELECT (
                SELECT AI.GENERATE_TEXT(
                    'Generate a brief security summary about cybersecurity threats'
                )
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Subquery AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Subquery AI.GENERATE_TEXT failed: {e}")
        
        # Test 4: Try using the functions with a CTE
        print("\n🧪 Test 4: CTE approach")
        try:
            query = """
            WITH ai_response AS (
                SELECT AI.GENERATE_TEXT(
                    'Generate a brief security summary about cybersecurity threats'
                ) as response
            )
            SELECT * FROM ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ CTE AI.GENERATE_TEXT query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ CTE AI.GENERATE_TEXT failed: {e}")
        
        # Test 5: Try using the functions with a different function name
        print("\n🧪 Test 5: Different function name approach")
        try:
            query = """
            SELECT ai.generate_text(
                'Generate a brief security summary about cybersecurity threats'
            ) as ai_response
            """
            
            job_config = bigquery.QueryJobConfig(dry_run=True)
            query_job = client.query(query, job_config=job_config)
            print(f"✅ Different function name query cost estimation successful")
            print(f"   Bytes processed: {query_job.total_bytes_processed}")
            
        except Exception as e:
            print(f"❌ Different function name failed: {e}")
        
        print("\n🎯 Alternative Approaches Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_alternative_approach()

