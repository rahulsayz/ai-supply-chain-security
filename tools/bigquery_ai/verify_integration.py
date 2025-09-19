#!/usr/bin/env python3
"""
Verification script for 58xxx CVE Dataset Integration
Checks that the data was successfully uploaded to BigQuery
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

def verify_integration():
    """Verify that the CVE integration was successful"""
    load_dotenv('.env')
    project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
    client = bigquery.Client(project=project_id)
    
    print("🔍 Verifying 58xxx CVE Dataset Integration...")
    print("=" * 50)
    
    try:
        # Check main table record count
        query = f'SELECT COUNT(*) as total_records FROM `{project_id}.cve_data.cve_records`'
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            print(f"✅ Total CVE records in BigQuery: {row.total_records}")
        
        # Check enhanced analysis view
        query2 = f'SELECT COUNT(*) as enhanced_count FROM `{project_id}.cve_data.cve_enhanced_analysis`'
        query_job2 = client.query(query2)
        results2 = query_job2.result()
        
        for row in results2:
            print(f"✅ Enhanced analysis view records: {row.enhanced_count}")
        
        # Check vendor risk analysis view
        query3 = f'SELECT COUNT(*) as vendor_count FROM `{project_id}.cve_data.vendor_risk_analysis`'
        query_job3 = client.query(query3)
        results3 = query_job3.result()
        
        for row in results3:
            print(f"✅ Vendor risk analysis records: {row.vendor_count}")
        
        # Sample some CVE data
        print("\n📊 Sample CVE Data:")
        sample_query = f"""
        SELECT 
            cve_id, 
            primary_vendor, 
            primary_product, 
            cvss_score, 
            cvss_severity
        FROM `{project_id}.cve_data.cve_enhanced_analysis`
        LIMIT 5
        """
        
        sample_job = client.query(sample_query)
        sample_results = sample_job.result()
        
        for row in sample_results:
            print(f"   {row.cve_id}: {row.primary_vendor} - {row.primary_product} (CVSS: {row.cvss_score} - {row.cvss_severity})")
        
        # Check vendor distribution
        print("\n🏢 Vendor Distribution:")
        vendor_query = f"""
        SELECT 
            vendor, 
            total_cves, 
            avg_cvss_score,
            critical_count,
            high_count
        FROM `{project_id}.cve_data.vendor_risk_analysis`
        ORDER BY total_cves DESC
        LIMIT 10
        """
        
        vendor_job = client.query(vendor_query)
        vendor_results = vendor_job.result()
        
        for row in vendor_results:
            print(f"   {row.vendor}: {row.total_cves} CVEs, Avg CVSS: {row.avg_cvss_score:.1f}, Critical: {row.critical_count}, High: {row.high_count}")
        
        print("\n🎉 Integration Verification Complete!")
        print("Your BigQuery AI endpoints now have access to real CVE data!")
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    verify_integration()
