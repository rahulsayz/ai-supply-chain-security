#!/usr/bin/env python3
"""
Check CVE Counts
Investigates why the enhanced view only shows 66 records instead of 149
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

def check_cve_counts():
    """Check CVE record counts"""
    load_dotenv('.env')
    project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
    client = bigquery.Client(project=project_id)
    
    print("🔍 Checking CVE Record Counts...")
    print("=" * 40)
    
    try:
        # Check total records
        query = f'SELECT COUNT(*) as total FROM `{project_id}.cve_data.cve_records`'
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            print(f"✅ Total CVE records: {row.total}")
        
        # Check records with CVSS scores
        query2 = f'SELECT COUNT(*) as total FROM `{project_id}.cve_data.cve_records` WHERE cvss_score IS NOT NULL'
        query_job2 = client.query(query2)
        results2 = query_job2.result()
        
        for row in results2:
            print(f"✅ Records with CVSS scores: {row.total}")
        
        # Check records without CVSS scores
        query3 = f'SELECT COUNT(*) as total FROM `{project_id}.cve_data.cve_records` WHERE cvss_score IS NULL'
        query_job3 = client.query(query3)
        results3 = query_job3.result()
        
        for row in results3:
            print(f"⚠️  Records without CVSS scores: {row.total}")
        
        # Sample some records without CVSS scores
        query4 = f'SELECT cve_id, descriptions FROM `{project_id}.cve_data.cve_records` WHERE cvss_score IS NULL LIMIT 3'
        query_job4 = client.query(query4)
        results4 = query_job4.result()
        
        print("\n📊 Sample records without CVSS scores:")
        for row in results4:
            print(f"   {row.cve_id}: {len(row.descriptions)} descriptions")
        
        # Check if the issue is with the enhanced view filter
        print("\n🔧 Enhanced View Analysis:")
        print("   The enhanced view filters by 'WHERE cvss_score IS NOT NULL'")
        print("   This means only records with CVSS scores are included")
        print("   Records without CVSS scores are excluded from analysis")
        
    except Exception as e:
        print(f"❌ Error checking CVE counts: {e}")

if __name__ == "__main__":
    check_cve_counts()
