# Test script to validate everything works:
from google.cloud import bigquery
import os

def test_bigquery_ai_setup():
    # Test 1: Basic connection
    client = bigquery.Client()
    print(f"✅ Connected to project: {client.project}")
    
    # Test 2: Dataset access
    dataset = client.get_dataset("supply_chain_demo")
    print(f"✅ Dataset accessible: {dataset.dataset_id}")
    
    # Test 3: AI function test
    query = """
    SELECT AI.GENERATE_TEXT(
        model => 'gemini-1.5-flash',
        prompt => 'Test: Generate a 10-word cybersecurity message'
    ) as test_result
    """
    
    result = client.query(query).result()
    for row in result:
        print(f"✅ BigQuery AI working: {row.test_result}")
    
    print("🎉 All tests passed! Ready for hackathon!")

if __name__ == "__main__":
    test_bigquery_ai_setup()