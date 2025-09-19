#!/usr/bin/env python3
"""
58xxx CVE Dataset Integration Script
Processes CVE JSON files from the 58xxx folder and integrates them with BigQuery
"""

import json
import os
import sys
import glob
from datetime import datetime
from typing import Dict, Any, List
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class CVE58xxxIntegrator:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
        self.client = None
        self.dataset_id = 'cve_data'
        self.table_id = 'cve_records'
        # Use absolute path to ensure it works from any working directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cve_folder = os.path.join(current_dir, '..', '..', '58xxx')
        
        # Try to initialize BigQuery client
        try:
            self.client = bigquery.Client(project=self.project_id)
            print("✅ BigQuery client initialized successfully")
        except Exception as e:
            print(f"❌ BigQuery client initialization failed: {e}")
            print("❌ Please ensure you have proper GCP credentials")
            sys.exit(1)
    
    def get_cve_files(self) -> List[str]:
        """Get all CVE JSON files from the 58xxx folder"""
        cve_path = os.path.join(self.cve_folder, '*.json')
        cve_files = glob.glob(cve_path)
        print(f"📁 Found {len(cve_files)} CVE files in {self.cve_folder}")
        return cve_files
    
    def parse_cve_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single CVE JSON file and extract relevant data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cve_data = json.load(f)
            
            # Extract basic CVE metadata
            cve_id = cve_data.get('cveMetadata', {}).get('cveId', '')
            state = cve_data.get('cveMetadata', {}).get('state', '')
            assigner_org_id = cve_data.get('cveMetadata', {}).get('assignerOrgId', '')
            assigner_short_name = cve_data.get('cveMetadata', {}).get('assignerShortName', '')
            date_reserved = cve_data.get('cveMetadata', {}).get('dateReserved')
            date_published = cve_data.get('cveMetadata', {}).get('datePublished')
            date_updated = cve_data.get('cveMetadata', {}).get('dateUpdated')
            
            # Extract CNA container data
            cna = cve_data.get('containers', {}).get('cna', {})
            
            # Extract affected products
            affected_products = []
            for affected in cna.get('affected', []):
                product_info = {
                    'vendor': affected.get('vendor', ''),
                    'product': affected.get('product', ''),
                    'platforms': affected.get('platforms', []),
                    'versions': []
                }
                
                for version in affected.get('versions', []):
                    version_info = {
                        'version': version.get('version', ''),
                        'status': version.get('status', ''),
                        'less_than_or_equal': version.get('lessThan', ''),
                        'version_type': version.get('versionType', '')
                    }
                    product_info['versions'].append(version_info)
                
                affected_products.append(product_info)
            
            # Extract descriptions
            descriptions = []
            for desc in cna.get('descriptions', []):
                descriptions.append({
                    'lang': desc.get('lang', 'en'),
                    'value': desc.get('value', '')
                })
            
            # Extract CVSS metrics
            cvss_score = None
            cvss_severity = None
            attack_vector = None
            attack_complexity = None
            privileges_required = None
            user_interaction = None
            scope = None
            confidentiality_impact = None
            integrity_impact = None
            availability_impact = None
            
            for metric in cna.get('metrics', []):
                if 'cvssV3_1' in metric:
                    cvss = metric['cvssV3_1']
                    cvss_score = cvss.get('baseScore')
                    cvss_severity = cvss.get('baseSeverity')
                    
                    # Parse vector string if available
                    vector_string = cvss.get('vectorString', '')
                    if vector_string:
                        parts = vector_string.split('/')
                        if len(parts) >= 6:
                            attack_vector = parts[1].split(':')[1] if ':' in parts[1] else parts[1]
                            attack_complexity = parts[2].split(':')[1] if ':' in parts[2] else parts[2]
                            privileges_required = parts[3].split(':')[1] if ':' in parts[3] else parts[3]
                            user_interaction = parts[4].split(':')[1] if ':' in parts[4] else parts[4]
                            scope = parts[5].split(':')[1] if ':' in parts[5] else parts[5]
                        if len(parts) >= 9:
                            confidentiality_impact = parts[6].split(':')[1] if ':' in parts[6] else parts[6]
                            integrity_impact = parts[7].split(':')[1] if ':' in parts[7] else parts[7]
                            availability_impact = parts[8].split(':')[1] if ':' in parts[8] else parts[8]
            
            # Extract CWE and CAPEC IDs
            cwe_ids = []
            capec_ids = []
            
            for problem_type in cna.get('problemTypes', []):
                for desc in problem_type.get('descriptions', []):
                    if desc.get('type') == 'CWE':
                        cwe_id = desc.get('cweId', '')
                        if cwe_id and cwe_id not in cwe_ids:
                            cwe_ids.append(cwe_id)
            
            # Extract references
            references = []
            for ref in cna.get('references', []):
                references.append({
                    'url': ref.get('url', ''),
                    'tags': ref.get('tags', [])
                })
            
            # Extract solutions (if available)
            solutions = []
            for solution in cna.get('solutions', []):
                solutions.append({
                    'lang': solution.get('lang', 'en'),
                    'value': solution.get('value', '')
                })
            
            # Create the processed CVE record
            current_time = datetime.now().isoformat() + "Z"
            processed_cve = {
                'cve_id': cve_id,
                'assigner_org_id': assigner_org_id,
                'state': state,
                'assigner_short_name': assigner_short_name,
                'date_reserved': date_reserved,
                'date_published': date_published,
                'date_updated': date_updated,
                'affected_products': affected_products,
                'descriptions': descriptions,
                'cvss_score': cvss_score,
                'cvss_severity': cvss_severity,
                'attack_vector': attack_vector,
                'attack_complexity': attack_complexity,
                'privileges_required': privileges_required,
                'user_interaction': user_interaction,
                'scope': scope,
                'confidentiality_impact': confidentiality_impact,
                'integrity_impact': integrity_impact,
                'availability_impact': availability_impact,
                'cwe_ids': cwe_ids,
                'capec_ids': capec_ids,
                'references': references,
                'solutions': solutions,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            return processed_cve
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def upload_to_bigquery(self, cve_records: List[Dict[str, Any]]) -> bool:
        """Upload CVE records to BigQuery"""
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            # Check if table exists
            try:
                table = self.client.get_table(table_ref)
                print(f"✅ Table {self.table_id} exists, will append data")
            except NotFound:
                print(f"❌ Table {self.table_id} not found. Please run setup_bigquery_cve.py first")
                return False
            
            # Prepare data for upload
            rows_to_insert = []
            for cve in cve_records:
                if cve:  # Skip None records
                    rows_to_insert.append(cve)
            
            if not rows_to_insert:
                print("❌ No valid CVE records to upload")
                return False
            
            # Upload data
            errors = self.client.insert_rows_json(table_ref, rows_to_insert)
            
            if errors:
                print(f"❌ Errors during upload: {errors}")
                return False
            
            print(f"✅ Successfully uploaded {len(rows_to_insert)} CVE records to BigQuery")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading to BigQuery: {e}")
            return False
    
    def create_enhanced_views(self):
        """Create enhanced views for better CVE analysis"""
        try:
            # Create enhanced CVE analysis view
            enhanced_view_query = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.cve_enhanced_analysis` AS
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
                descriptions[OFFSET(0)].value as primary_description,
                affected_products[OFFSET(0)].vendor as primary_vendor,
                affected_products[OFFSET(0)].product as primary_product,
                cwe_ids,
                capec_ids,
                affected_products,
                references,
                solutions
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE cvss_score IS NOT NULL
            """
            
            # Create vendor risk analysis view
            vendor_risk_view_query = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.vendor_risk_analysis` AS
            SELECT 
                affected_products[OFFSET(0)].vendor as vendor,
                COUNT(*) as total_cves,
                AVG(cvss_score) as avg_cvss_score,
                COUNTIF(cvss_severity = 'CRITICAL') as critical_count,
                COUNTIF(cvss_severity = 'HIGH') as high_count,
                COUNTIF(cvss_severity = 'MEDIUM') as medium_count,
                COUNTIF(cvss_severity = 'LOW') as low_count,
                ARRAY_AGG(DISTINCT cve_id) as cve_ids,
                ARRAY_AGG(DISTINCT affected_products[OFFSET(0)].product) as products
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            WHERE affected_products[OFFSET(0)].vendor IS NOT NULL
            GROUP BY affected_products[OFFSET(0)].vendor
            """
            
            # Execute view creation
            self.client.query(enhanced_view_query).result()
            print("✅ Created enhanced CVE analysis view")
            
            self.client.query(vendor_risk_view_query).result()
            print("✅ Created vendor risk analysis view")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating enhanced views: {e}")
            return False
    
    def run_integration(self):
        """Run the complete CVE integration process"""
        print("🚀 Starting 58xxx CVE Dataset Integration...")
        print("=" * 60)
        
        # Get CVE files
        cve_files = self.get_cve_files()
        if not cve_files:
            print("❌ No CVE files found")
            return
        
        # Parse CVE files
        print("\n📊 Parsing CVE files...")
        cve_records = []
        for file_path in cve_files:
            cve_record = self.parse_cve_file(file_path)
            if cve_record:
                cve_records.append(cve_record)
        
        print(f"✅ Parsed {len(cve_records)} valid CVE records")
        
        # Upload to BigQuery
        print("\n☁️ Uploading to BigQuery...")
        if self.upload_to_bigquery(cve_records):
            # Create enhanced views
            print("\n🔍 Creating enhanced analysis views...")
            self.create_enhanced_views()
            
            print("\n🎉 CVE Integration Complete!")
            print(f"📊 Total CVE records: {len(cve_records)}")
            print(f"🔍 Enhanced views created for analysis")
            print(f"📈 Your existing BigQuery AI endpoints now have access to real CVE data!")
        else:
            print("\n❌ CVE Integration failed")

def main():
    """Main function"""
    integrator = CVE58xxxIntegrator()
    integrator.run_integration()

if __name__ == "__main__":
    main()
