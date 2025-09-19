#!/usr/bin/env python3
"""
Test CVE Data Access
Checks if the uploaded CVE data is accessible from BigQuery
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

def test_cve_data_access():
    """Test if CVE data is accessible"""
    load_dotenv('.env')
    project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
    client = bigquery.Client(project=project_id)
    
    print("🔍 Testing CVE Data Access...")
    print("=" * 40)
    
    try:
        # Test 1: Check if we can query the CVE data directly
        query = f'SELECT cve_id, primary_vendor, cvss_score, cvss_severity FROM `{project_id}.cve_data.cve_enhanced_analysis` WHERE cve_id = "CVE-2024-58249" LIMIT 1'
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            print(f"✅ Found CVE data: {row.cve_id} - {row.primary_vendor} - CVSS {row.cvss_score} ({row.cvss_severity})")
        
        # Test 2: Check total count
        count_query = f'SELECT COUNT(*) as total FROM `{project_id}.cve_data.cve_records`'
        count_job = client.query(count_query)
        count_results = count_job.result()
        
        for row in count_results:
            print(f"✅ Total CVE records: {row.total}")
        
        # Test 3: Check if the CVE processor can access this data
        print("\n🔧 Testing CVE Processor Integration...")
        
        # Import and test the CVE processor
        from cve_processor import CVEProcessor
        processor = CVEProcessor()
        
        # Test threat analysis
        result = processor.analyze_threat_with_ai("CVE-2024-58249")
        if result.get("success") and "cve_data" in result.get("data", {}):
            print("✅ CVE processor successfully accessed real CVE data")
            cve_data = result["data"]["cve_data"]
            print(f"   CVE ID: {cve_data.get('cve_id')}")
            print(f"   Vendor: {cve_data.get('vendor')}")
            print(f"   CVSS Score: {cve_data.get('cvss_score')}")
        else:
            print("❌ CVE processor still returning demo data")
            print(f"   Response: {result}")
        
    except Exception as e:
        print(f"❌ Error testing CVE data access: {e}")

if __name__ == "__main__":
    test_cve_data_access()
