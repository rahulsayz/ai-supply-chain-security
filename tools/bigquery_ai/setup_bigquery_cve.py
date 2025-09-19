#!/usr/bin/env python3
"""
BigQuery CVE Data Setup Script
Creates dataset, tables, and sample CVE data for Supply Chain Security application
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

class BigQueryCVESetup:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', 'ai-sales-agent-452915')
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_id = 'cve_data'
        self.table_id = 'cve_records'
        
    def create_dataset(self):
        """Create the CVE dataset if it doesn't exist"""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            dataset = self.client.get_dataset(dataset_ref)
            print(f"✅ Dataset {self.dataset_id} already exists")
            return dataset
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # Set location
            dataset.description = "CVE vulnerability data for supply chain security analysis"
            
            dataset = self.client.create_dataset(dataset, timeout=30)
            print(f"✅ Created dataset {self.dataset_id}")
            return dataset
    
    def create_cve_table(self):
        """Create the CVE records table with proper schema"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        # Define the schema for CVE data
        schema = [
            bigquery.SchemaField("cve_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("assigner_org_id", "STRING"),
            bigquery.SchemaField("state", "STRING"),
            bigquery.SchemaField("assigner_short_name", "STRING"),
            bigquery.SchemaField("date_reserved", "TIMESTAMP"),
            bigquery.SchemaField("date_published", "TIMESTAMP"),
            bigquery.SchemaField("date_updated", "TIMESTAMP"),
            
            # Affected products - nested array
            bigquery.SchemaField("affected_products", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("vendor", "STRING"),
                bigquery.SchemaField("product", "STRING"),
                bigquery.SchemaField("platforms", "STRING", mode="REPEATED"),
                bigquery.SchemaField("versions", "RECORD", mode="REPEATED", fields=[
                    bigquery.SchemaField("version", "STRING"),
                    bigquery.SchemaField("status", "STRING"),
                    bigquery.SchemaField("less_than_or_equal", "STRING"),
                    bigquery.SchemaField("version_type", "STRING")
                ])
            ]),
            
            # Descriptions
            bigquery.SchemaField("descriptions", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("lang", "STRING"),
                bigquery.SchemaField("value", "STRING")
            ]),
            
            # CVSS Metrics
            bigquery.SchemaField("cvss_score", "FLOAT64"),
            bigquery.SchemaField("cvss_severity", "STRING"),
            bigquery.SchemaField("attack_vector", "STRING"),
            bigquery.SchemaField("attack_complexity", "STRING"),
            bigquery.SchemaField("privileges_required", "STRING"),
            bigquery.SchemaField("user_interaction", "STRING"),
            bigquery.SchemaField("scope", "STRING"),
            bigquery.SchemaField("confidentiality_impact", "STRING"),
            bigquery.SchemaField("integrity_impact", "STRING"),
            bigquery.SchemaField("availability_impact", "STRING"),
            
            # CWE and CAPEC
            bigquery.SchemaField("cwe_ids", "STRING", mode="REPEATED"),
            bigquery.SchemaField("capec_ids", "STRING", mode="REPEATED"),
            
            # References and solutions
            bigquery.SchemaField("references", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("url", "STRING"),
                bigquery.SchemaField("tags", "STRING", mode="REPEATED")
            ]),
            bigquery.SchemaField("solutions", "RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("lang", "STRING"),
                bigquery.SchemaField("value", "STRING")
            ]),
            
            # Timestamps
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED")
        ]
        
        try:
            table = self.client.get_table(table_ref)
            print(f"✅ Table {self.table_id} already exists")
            return table
        except NotFound:
            table = bigquery.Table(table_ref, schema=schema)
            table.description = "CVE vulnerability records with AI-ready structure"
            
            table = self.client.create_table(table, timeout=30)
            print(f"✅ Created table {self.table_id}")
            return table
    
    def generate_sample_cve_data(self) -> List[Dict[str, Any]]:
        """Generate realistic sample CVE data for testing"""
        sample_cves = []
        
        # Base CVE data
        base_cves = [
            {
                "cve_id": "CVE-2024-0001",
                "assigner_short_name": "PureStorage",
                "cvss_score": 10.0,
                "cvss_severity": "CRITICAL",
                "attack_vector": "NETWORK",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "scope": "CHANGED",
                "confidentiality_impact": "HIGH",
                "integrity_impact": "HIGH",
                "availability_impact": "HIGH",
                "cwe_ids": ["CWE-1188"],
                "capec_ids": ["CAPEC-233"],
                "vendor": "Pure Storage",
                "product": "FlashArray",
                "description": "A condition exists in FlashArray Purity whereby a local account intended for initial array configuration remains active potentially allowing a malicious actor to gain elevated privileges."
            },
            {
                "cve_id": "CVE-2024-0002",
                "assigner_short_name": "Microsoft",
                "cvss_score": 9.8,
                "cvss_severity": "CRITICAL",
                "attack_vector": "NETWORK",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "scope": "CHANGED",
                "confidentiality_impact": "HIGH",
                "integrity_impact": "HIGH",
                "availability_impact": "HIGH",
                "cwe_ids": ["CWE-787", "CWE-125"],
                "capec_ids": ["CAPEC-100"],
                "vendor": "Microsoft",
                "product": "Windows",
                "description": "A remote code execution vulnerability exists in Windows when the Windows Imaging Component improperly handles objects in memory."
            },
            {
                "cve_id": "CVE-2024-0003",
                "assigner_short_name": "Oracle",
                "cvss_score": 8.5,
                "cvss_severity": "HIGH",
                "attack_vector": "NETWORK",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "REQUIRED",
                "scope": "CHANGED",
                "confidentiality_impact": "HIGH",
                "integrity_impact": "NONE",
                "availability_impact": "NONE",
                "cwe_ids": ["CWE-79"],
                "capec_ids": ["CAPEC-66"],
                "vendor": "Oracle",
                "product": "Java",
                "description": "A cross-site scripting vulnerability in Oracle Java SE allows remote attackers to inject arbitrary web script or HTML via crafted input."
            },
            {
                "cve_id": "CVE-2024-0004",
                "assigner_short_name": "Cisco",
                "cvss_score": 7.5,
                "cvss_severity": "HIGH",
                "attack_vector": "NETWORK",
                "attack_complexity": "LOW",
                "privileges_required": "NONE",
                "user_interaction": "NONE",
                "scope": "UNCHANGED",
                "confidentiality_impact": "NONE",
                "integrity_impact": "NONE",
                "availability_impact": "HIGH",
                "cwe_ids": ["CWE-400"],
                "capec_ids": ["CAPEC-125"],
                "vendor": "Cisco",
                "product": "IOS XE",
                "description": "A denial of service vulnerability in Cisco IOS XE Software could allow an unauthenticated, remote attacker to cause the device to reload."
            },
            {
                "cve_id": "CVE-2024-0005",
                "assigner_short_name": "VMware",
                "cvss_score": 6.5,
                "cvss_severity": "MEDIUM",
                "attack_vector": "NETWORK",
                "attack_complexity": "LOW",
                "privileges_required": "LOW",
                "user_interaction": "NONE",
                "scope": "UNCHANGED",
                "confidentiality_impact": "LOW",
                "integrity_impact": "NONE",
                "availability_impact": "NONE",
                "cwe_ids": ["CWE-200"],
                "capec_ids": ["CAPEC-116"],
                "vendor": "VMware",
                "product": "vCenter",
                "description": "An information disclosure vulnerability in VMware vCenter Server could allow an attacker to access sensitive information."
            }
        ]
        
        # Generate additional CVE records with variations
        for i, base_cve in enumerate(base_cves):
            # Create variations with different dates and minor changes
            for j in range(3):  # 3 variations per base CVE
                cve_id = f"{base_cve['cve_id']}-{chr(97+j)}"  # CVE-2024-0001-a, CVE-2024-0001-b, etc.
                
                # Vary the CVSS score slightly
                cvss_variation = base_cve['cvss_score'] + (j * 0.1) - 0.1
                cvss_variation = max(0.0, min(10.0, cvss_variation))
                
                # Vary the dates
                base_date = datetime.now() - timedelta(days=30 + (i * 7) + j)
                
                cve_record = {
                    "cve_id": cve_id,
                    "assigner_org_id": f"org-{i:04d}-{j:02d}",
                    "state": "PUBLISHED",
                    "assigner_short_name": base_cve['assigner_short_name'],
                    "date_reserved": (base_date - timedelta(days=30)).isoformat() + "Z",
                    "date_published": base_date.isoformat() + "Z",
                    "date_updated": (base_date + timedelta(days=1)).isoformat() + "Z",
                    
                    "affected_products": [{
                        "vendor": base_cve['vendor'],
                        "product": base_cve['product'],
                        "platforms": ["Linux", "Windows", "macOS"],
                        "versions": [{
                            "version": "1.0.0",
                            "status": "affected",
                            "less_than_or_equal": "2.0.0",
                            "version_type": "semver"
                        }]
                    }],
                    
                    "descriptions": [{
                        "lang": "en",
                        "value": base_cve['description']
                    }],
                    
                    "cvss_score": cvss_variation,
                    "cvss_severity": base_cve['cvss_severity'],
                    "attack_vector": base_cve['attack_vector'],
                    "attack_complexity": base_cve['attack_complexity'],
                    "privileges_required": base_cve['privileges_required'],
                    "user_interaction": base_cve['user_interaction'],
                    "scope": base_cve['scope'],
                    "confidentiality_impact": base_cve['confidentiality_impact'],
                    "integrity_impact": base_cve['integrity_impact'],
                    "availability_impact": base_cve['availability_impact'],
                    
                    "cwe_ids": base_cve['cwe_ids'],
                    "capec_ids": base_cve['capec_ids'],
                    
                    "references": [{
                        "url": f"https://example.com/security/{cve_id}",
                        "tags": ["vendor-advisory", "security-bulletin"]
                    }],
                    
                    "solutions": [{
                        "lang": "en",
                        "value": f"Update to the latest version of {base_cve['product']} to resolve this vulnerability."
                    }],
                    
                    "created_at": datetime.now().isoformat() + "Z",
                    "updated_at": datetime.now().isoformat() + "Z"
                }
                
                sample_cves.append(cve_record)
        
        return sample_cves
    
    def insert_sample_data(self, sample_data: List[Dict[str, Any]]):
        """Insert sample CVE data into BigQuery"""
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        # Convert the data to BigQuery format
        rows_to_insert = []
        for cve in sample_data:
            # Flatten nested structures for BigQuery
            row = {
                "cve_id": cve["cve_id"],
                "assigner_org_id": cve["assigner_org_id"],
                "state": cve["state"],
                "assigner_short_name": cve["assigner_short_name"],
                "date_reserved": cve["date_reserved"],
                "date_published": cve["date_published"],
                "date_updated": cve["date_updated"],
                "affected_products": cve["affected_products"],
                "descriptions": cve["descriptions"],
                "cvss_score": cve["cvss_score"],
                "cvss_severity": cve["cvss_severity"],
                "attack_vector": cve["attack_vector"],
                "attack_complexity": cve["attack_complexity"],
                "privileges_required": cve["privileges_required"],
                "user_interaction": cve["user_interaction"],
                "scope": cve["scope"],
                "confidentiality_impact": cve["confidentiality_impact"],
                "integrity_impact": cve["integrity_impact"],
                "availability_impact": cve["availability_impact"],
                "cwe_ids": cve["cwe_ids"],
                "capec_ids": cve["capec_ids"],
                "references": cve["references"],
                "solutions": cve["solutions"],
                "created_at": cve["created_at"],
                "updated_at": cve["updated_at"]
            }
            rows_to_insert.append(row)
        
        # Insert data
        errors = self.client.insert_rows_json(table_ref, rows_to_insert)
        if errors:
            print(f"❌ Errors inserting data: {errors}")
        else:
            print(f"✅ Successfully inserted {len(rows_to_insert)} CVE records")
    
    def create_ai_views(self):
        """Create AI-ready views for BigQuery AI functions"""
        views = [
            {
                "name": "cve_ai_analysis",
                "query": f"""
                CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.cve_ai_analysis` AS
                SELECT 
                    cve_id,
                    assigner_short_name as vendor,
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
                    cwe_ids,
                    capec_ids,
                    descriptions[OFFSET(0)].value as description,
                    affected_products[OFFSET(0)].product as product,
                    affected_products[OFFSET(0)].vendor as product_vendor,
                    date_published,
                    date_updated,
                    created_at
                FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
                WHERE state = 'PUBLISHED'
                """
            },
            {
                "name": "cve_risk_matrix",
                "query": f"""
                CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.cve_risk_matrix` AS
                SELECT 
                    cve_id,
                    vendor,
                    product,
                    cvss_score,
                    cvss_severity,
                    CASE 
                        WHEN cvss_score >= 9.0 THEN 'CRITICAL'
                        WHEN cvss_score >= 7.0 THEN 'HIGH'
                        WHEN cvss_score >= 4.0 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END as risk_level,
                    attack_vector,
                    attack_complexity,
                    user_interaction,
                    scope,
                    description,
                    date_published,
                    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), date_published, DAY) as days_since_published
                FROM `{self.project_id}.{self.dataset_id}.cve_ai_analysis`
                """
            }
        ]
        
        for view in views:
            try:
                query_job = self.client.query(view["query"])
                query_job.result()  # Wait for completion
                print(f"✅ Created view: {view['name']}")
            except Exception as e:
                print(f"❌ Error creating view {view['name']}: {e}")
    
    def test_ai_functions(self):
        """Test BigQuery AI functions with the CVE data"""
        print("\n🧪 Testing BigQuery AI Functions...")
        
        # Test 1: Basic query to verify data is accessible
        test_query1 = f"""
        SELECT 
            cve_id,
            vendor,
            cvss_score,
            description
        FROM `{self.project_id}.{self.dataset_id}.cve_ai_analysis`
        LIMIT 3
        """
        
        try:
            query_job = self.client.query(test_query1)
            results = query_job.result()
            print("✅ Basic CVE data query successful")
            for row in results:
                print(f"   {row.cve_id}: {row.vendor} - CVSS {row.cvss_score}")
        except Exception as e:
            print(f"❌ Basic query test failed: {e}")
        
        # Test 2: Risk matrix view
        test_query2 = f"""
        SELECT 
            cve_id,
            risk_level,
            cvss_score,
            vendor
        FROM `{self.project_id}.{self.dataset_id}.cve_risk_matrix`
        WHERE risk_level = 'CRITICAL'
        LIMIT 3
        """
        
        try:
            query_job = self.client.query(test_query2)
            results = query_job.result()
            print("✅ Risk matrix view test successful")
            for row in results:
                print(f"   {row.cve_id}: {row.risk_level} - {row.vendor}")
        except Exception as e:
            print(f"❌ Risk matrix test failed: {e}")
    
    def run_setup(self):
        """Run the complete BigQuery setup"""
        print("🚀 Setting up BigQuery for CVE data...")
        print(f"Project ID: {self.project_id}")
        
        try:
            # Step 1: Create dataset
            self.create_dataset()
            
            # Step 2: Create table
            self.create_cve_table()
            
            # Step 3: Generate sample data
            print("📊 Generating sample CVE data...")
            sample_data = self.generate_sample_cve_data()
            print(f"Generated {len(sample_data)} sample CVE records")
            
            # Step 4: Insert sample data
            print("💾 Inserting sample data into BigQuery...")
            self.insert_sample_data(sample_data)
            
            # Step 5: Create AI-ready views
            print("🔧 Creating AI-ready views...")
            self.create_ai_views()
            
            # Step 6: Test basic functionality
            self.test_ai_functions()
            
            print("\n🎉 BigQuery CVE setup completed successfully!")
            print(f"Dataset: {self.project_id}.{self.dataset_id}")
            print(f"Table: {self.project_id}.{self.dataset_id}.{self.table_id}")
            print(f"Views: cve_ai_analysis, cve_risk_matrix")
            print("\n📝 Note: AI functions require BigQuery AI features to be enabled in your project.")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    setup = BigQueryCVESetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
