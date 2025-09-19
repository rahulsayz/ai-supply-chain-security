#!/usr/bin/env python3
"""
Debug Threat Analysis
Shows exactly what's happening when analyze_threat is called
"""

from minimal_ai_processor import EnhancedAIProcessor
import traceback

def debug_threat_analysis():
    """Debug the threat analysis process"""
    print("🔍 Debugging Threat Analysis...")
    print("=" * 50)
    
    try:
        # Create processor
        processor = EnhancedAIProcessor()
        print(f"✅ Processor created: {type(processor)}")
        print(f"✅ CVE processor available: {processor.cve_processor is not None}")
        
        if processor.cve_processor:
            print(f"✅ CVE processor type: {type(processor.cve_processor)}")
            
            # Test CVE costs first
            print("\n🔧 Testing CVE costs...")
            try:
                costs = processor.cve_processor.get_cve_costs()
                print(f"✅ CVE costs successful: {costs.get('success', False)}")
                if 'cve_statistics' in costs:
                    print(f"✅ CVE statistics available: {costs['cve_statistics']}")
            except Exception as e:
                print(f"❌ CVE costs failed: {e}")
                print(f"❌ Traceback: {traceback.format_exc()}")
            
            # Test threat analysis
            print("\n🔧 Testing threat analysis...")
            try:
                result = processor.analyze_threat("CVE-2024-58249")
                print(f"✅ Threat analysis successful: {result.get('success', False)}")
                if result.get('success'):
                    print(f"✅ Query type: {result.get('data', {}).get('query_type', 'Unknown')}")
                    if 'cve_data' in result.get('data', {}):
                        print(f"✅ CVE data present: {result['data']['cve_data']}")
                    else:
                        print("❌ No CVE data in response")
                else:
                    print(f"❌ Threat analysis failed: {result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Threat analysis exception: {e}")
                print(f"❌ Traceback: {traceback.format_exc()}")
        else:
            print("❌ CVE processor not available")
            
    except Exception as e:
        print(f"❌ Main exception: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_threat_analysis()
