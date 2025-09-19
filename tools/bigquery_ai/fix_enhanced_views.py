#!/usr/bin/env python3
"""
Fix Enhanced Views Script
Creates robust enhanced views for the 58xxx CVE dataset
"""

from google.cloud import bigquery
import os
from dotenv import load_dotenv

def fix_enhanced_views():
    """Fix the enhanced views with proper error handling"""
    load_dotenv('.env')
    project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
    client = bigquery.Client(project=project_id)
    
    print("🔧 Fixing Enhanced Views...")
    print("=" * 40)
    
    try:
        # Create a simpler, more robust enhanced CVE analysis view
        enhanced_view_query = f"""
        CREATE OR REPLACE VIEW `{project_id}.cve_data.cve_enhanced_analysis` AS
        SELECT 
            cve_id,
            assigner_short_name,
            state,
            date_published,
            date_updated,
            cvss_score,
            cvss_severity,
            attack_vector,
            attack_complexity,
            privileges_required,
            user_interaction,
            scope,
            confidentiality_impact,
            integrity_impact,
            availability_impact,
            ARRAY_LENGTH(cwe_ids) as cwe_count,
            ARRAY_LENGTH(capec_ids) as capec_count,
            ARRAY_LENGTH(affected_products) as affected_product_count,
            ARRAY_LENGTH(references) as reference_count,
            -- Safe array access with fallbacks
            CASE 
                WHEN ARRAY_LENGTH(descriptions) > 0 THEN descriptions[OFFSET(0)].value
                ELSE 'No description available'
            END as primary_description,
            CASE 
                WHEN ARRAY_LENGTH(affected_products) > 0 THEN affected_products[OFFSET(0)].vendor
                ELSE 'Unknown Vendor'
            END as primary_vendor,
            CASE 
                WHEN ARRAY_LENGTH(affected_products) > 0 THEN affected_products[OFFSET(0)].product
                ELSE 'Unknown Product'
            END as primary_product,
            cwe_ids,
            capec_ids,
            affected_products,
            references,
            solutions
        FROM `{project_id}.cve_data.cve_records`
        WHERE cvss_score IS NOT NULL
        """
        
        # Execute view creation
        client.query(enhanced_view_query).result()
        print("✅ Enhanced CVE analysis view created successfully")
        
        # Create vendor risk analysis view
        vendor_risk_view_query = f"""
        CREATE OR REPLACE VIEW `{project_id}.cve_data.vendor_risk_analysis` AS
        SELECT 
            CASE 
                WHEN ARRAY_LENGTH(affected_products) > 0 THEN affected_products[OFFSET(0)].vendor
                ELSE 'Unknown Vendor'
            END as vendor,
            COUNT(*) as total_cves,
            AVG(cvss_score) as avg_cvss_score,
            COUNTIF(cvss_severity = 'CRITICAL') as critical_count,
            COUNTIF(cvss_severity = 'HIGH') as high_count,
            COUNTIF(cvss_severity = 'MEDIUM') as medium_count,
            COUNTIF(cvss_severity = 'LOW') as low_count,
            ARRAY_AGG(DISTINCT cve_id) as cve_ids,
            ARRAY_AGG(DISTINCT 
                CASE 
                    WHEN ARRAY_LENGTH(affected_products) > 0 THEN affected_products[OFFSET(0)].product
                    ELSE 'Unknown Product'
                END
            ) as products
        FROM `{project_id}.cve_data.cve_records`
        WHERE cvss_score IS NOT NULL
        GROUP BY 
            CASE 
                WHEN ARRAY_LENGTH(affected_products) > 0 THEN affected_products[OFFSET(0)].vendor
                ELSE 'Unknown Vendor'
            END
        """
        
        # Execute vendor view creation
        client.query(vendor_risk_view_query).result()
        print("✅ Vendor risk analysis view created successfully")
        
        print("\n🎉 All enhanced views fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing enhanced views: {e}")
        return False

if __name__ == "__main__":
    fix_enhanced_views()
