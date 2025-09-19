#!/usr/bin/env python3
"""
Test script for 58xxx CVE Dataset Integration
Verifies that the integration can process and analyze the CVE data
"""

import json
import os
import sys
from pathlib import Path

def test_cve_file_parsing():
    """Test parsing of individual CVE files"""
    print("🧪 Testing CVE file parsing...")
    
    # Use absolute path to ensure it works from any working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cve_folder = Path(os.path.join(current_dir, '..', '..', '58xxx'))
    if not cve_folder.exists():
        print("❌ 58xxx folder not found")
        return False
    
    # Get a few sample files
    cve_files = list(cve_folder.glob("*.json"))[:5]  # Test first 5 files
    
    if not cve_files:
        print("❌ No CVE files found")
        return False
    
    print(f"📁 Found {len(cve_files)} CVE files to test")
    
    for cve_file in cve_files:
        try:
            with open(cve_file, 'r', encoding='utf-8') as f:
                cve_data = json.load(f)
            
            # Basic validation
            cve_id = cve_data.get('cveMetadata', {}).get('cveId', '')
            state = cve_data.get('cveMetadata', {}).get('state', '')
            descriptions = cve_data.get('containers', {}).get('cna', {}).get('descriptions', [])
            
            if not cve_id:
                print(f"❌ {cve_file.name}: Missing CVE ID")
                continue
            
            if not descriptions:
                print(f"❌ {cve_file.name}: Missing descriptions")
                continue
            
            # Check CVSS data
            metrics = cve_data.get('containers', {}).get('cna', {}).get('metrics', [])
            cvss_found = False
            for metric in metrics:
                if 'cvssV3_1' in metric:
                    cvss_found = True
                    cvss_score = metric['cvssV3_1'].get('baseScore')
                    cvss_severity = metric['cvssV3_1'].get('baseSeverity')
                    print(f"✅ {cve_id}: CVSS {cvss_score} ({cvss_severity})")
                    break
            
            if not cvss_found:
                print(f"⚠️  {cve_id}: No CVSS data found")
            
            # Check affected products
            affected = cve_data.get('containers', {}).get('cna', {}).get('affected', [])
            if affected:
                vendor = affected[0].get('vendor', 'Unknown')
                product = affected[0].get('product', 'Unknown')
                print(f"   📦 Vendor: {vendor}, Product: {product}")
            
        except Exception as e:
            print(f"❌ Error parsing {cve_file.name}: {e}")
            return False
    
    print("✅ CVE file parsing test completed")
    return True

def test_data_structure():
    """Test the expected data structure for BigQuery"""
    print("\n🔍 Testing data structure compatibility...")
    
    # Use absolute path to ensure it works from any working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Sample CVE file
    cve_file = Path(os.path.join(current_dir, '..', '..', '58xxx', 'CVE-2024-58249.json'))
    if not cve_file.exists():
        print("❌ Sample CVE file not found")
        return False
    
    try:
        with open(cve_file, 'r', encoding='utf-8') as f:
            cve_data = json.load(f)
        
        # Extract key fields that will be mapped to BigQuery
        cve_id = cve_data.get('cveMetadata', {}).get('cveId', '')
        state = cve_data.get('cveMetadata', {}).get('state', '')
        assigner = cve_data.get('cveMetadata', {}).get('assignerShortName', '')
        
        cna = cve_data.get('containers', {}).get('cna', {})
        descriptions = cna.get('descriptions', [])
        affected = cna.get('affected', [])
        metrics = cna.get('metrics', [])
        problem_types = cna.get('problemTypes', [])
        references = cna.get('references', [])
        
        print(f"📊 Data structure analysis for {cve_id}:")
        print(f"   State: {state}")
        print(f"   Assigner: {assigner}")
        print(f"   Descriptions: {len(descriptions)}")
        print(f"   Affected products: {len(affected)}")
        print(f"   CVSS metrics: {len(metrics)}")
        print(f"   Problem types: {len(problem_types)}")
        print(f"   References: {len(references)}")
        
        # Check if we have the minimum required data
        if cve_id and descriptions and affected:
            print("✅ Data structure is compatible with BigQuery schema")
            return True
        else:
            print("❌ Missing required data fields")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing data structure: {e}")
        return False

def test_bigquery_schema_compatibility():
    """Test if the data can be mapped to BigQuery schema"""
    print("\n🗄️ Testing BigQuery schema compatibility...")
    
    # Expected BigQuery fields
    expected_fields = [
        'cve_id', 'state', 'assigner_short_name', 'date_published',
        'cvss_score', 'cvss_severity', 'attack_vector', 'primary_vendor', 'primary_product'
    ]
    
    print("📋 Expected BigQuery fields:")
    for field in expected_fields:
        print(f"   ✅ {field}")
    
    # Use absolute path to ensure it works from any working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Test data mapping
    cve_file = Path(os.path.join(current_dir, '..', '..', '58xxx', 'CVE-2024-58249.json'))
    if not cve_file.exists():
        print("❌ Sample CVE file not found")
        return False
    
    try:
        with open(cve_file, 'r', encoding='utf-8') as f:
            cve_data = json.load(f)
        
        # Simulate the mapping that will happen in the integration
        mapped_data = {
            'cve_id': cve_data.get('cveMetadata', {}).get('cveId', ''),
            'state': cve_data.get('cveMetadata', {}).get('state', ''),
            'assigner_short_name': cve_data.get('cveMetadata', {}).get('assignerShortName', ''),
            'date_published': cve_data.get('cveMetadata', {}).get('datePublished', ''),
            'cvss_score': None,
            'cvss_severity': None,
            'attack_vector': None,
            'primary_vendor': None,
            'primary_product': None
        }
        
        # Extract CVSS data
        metrics = cve_data.get('containers', {}).get('cna', {}).get('metrics', [])
        for metric in metrics:
            if 'cvssV3_1' in metric:
                cvss = metric['cvssV3_1']
                mapped_data['cvss_score'] = cvss.get('baseScore')
                mapped_data['cvss_severity'] = cvss.get('baseSeverity')
                
                # Parse vector string for attack vector
                vector_string = cvss.get('vectorString', '')
                if vector_string and '/' in vector_string:
                    parts = vector_string.split('/')
                    if len(parts) > 1:
                        mapped_data['attack_vector'] = parts[1].split(':')[1] if ':' in parts[1] else parts[1]
                break
        
        # Extract vendor and product
        affected = cve_data.get('containers', {}).get('cna', {}).get('affected', [])
        if affected:
            mapped_data['primary_vendor'] = affected[0].get('vendor', '')
            mapped_data['primary_product'] = affected[0].get('product', '')
        
        print("\n📊 Mapped data sample:")
        for field, value in mapped_data.items():
            status = "✅" if value is not None else "⚠️"
            print(f"   {status} {field}: {value}")
        
        # Check if we have the essential fields
        essential_fields = ['cve_id', 'cvss_score', 'primary_vendor']
        missing_essential = [field for field in essential_fields if not mapped_data.get(field)]
        
        if missing_essential:
            print(f"❌ Missing essential fields: {missing_essential}")
            return False
        else:
            print("✅ All essential fields are mapped correctly")
            return True
            
    except Exception as e:
        print(f"❌ Error testing schema compatibility: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 58xxx CVE Dataset Integration Tests")
    print("=" * 50)
    
    tests = [
        test_cve_file_parsing,
        test_data_structure,
        test_bigquery_schema_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The 58xxx CVE dataset is ready for integration.")
        print("\n🔧 Next steps:")
        print("1. Ensure BigQuery credentials are configured")
        print("2. Run: python integrate_58xxx_cve.py")
        print("3. Your existing BigQuery AI endpoints will have access to real CVE data!")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
