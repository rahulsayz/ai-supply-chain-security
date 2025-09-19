#!/usr/bin/env python3
"""
Test script for BigQuery Billing API integration
"""
import os
import sys
from datetime import datetime

# Set the correct project ID for testing
os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from billing_service import get_billing_service
from rich.console import Console

console = Console()

def test_billing_api():
    """Test the BigQuery Billing API integration"""
    console.print("🏦 Testing BigQuery Billing API Integration")
    console.print("=" * 60)
    
    try:
        billing_service = get_billing_service()
        
        # Test billing account access
        console.print("🔍 Testing billing account access...")
        billing_account = billing_service.get_billing_account()
        
        if billing_account:
            console.print(f"✅ Billing account found: {billing_account}")
        else:
            console.print("❌ No billing account available")
            console.print("💡 This is expected if the service account doesn't have billing permissions")
            console.print("💡 The system will fall back to estimated costs based on BigQuery usage")
            
        # Test BigQuery cost estimation (this should work even without billing access)
        console.print("\n💰 Testing BigQuery cost estimation...")
        costs = billing_service.get_real_time_costs(days=7)
        
        if "error" in costs:
            console.print(f"❌ Error getting costs: {costs['error']}")
        else:
            console.print("✅ BigQuery costs retrieved successfully")
            bigquery_costs = costs.get('bigquery_costs', {})
            if "error" not in bigquery_costs:
                console.print(f"   Total BigQuery cost: ${bigquery_costs.get('total_cost', 0):.4f}")
                console.print(f"   Data processing: ${bigquery_costs.get('bytes_cost', 0):.4f}")
                console.print(f"   Compute slots: ${bigquery_costs.get('slots_cost', 0):.4f}")
                console.print(f"   Jobs processed: {bigquery_costs.get('job_count', 0)}")
            else:
                console.print(f"   BigQuery costs: {bigquery_costs.get('error', 'Unknown error')}")
                
        # Test daily cost breakdown
        console.print("\n📅 Testing daily cost breakdown...")
        daily_costs = billing_service.get_daily_cost_breakdown()
        
        if "error" in daily_costs:
            console.print(f"❌ Error getting daily costs: {daily_costs['error']}")
        else:
            console.print("✅ Daily cost breakdown retrieved")
            console.print(f"   Date: {daily_costs['date']}")
            console.print(f"   Total cost: ${daily_costs['total_cost']:.4f}")
            if 'cost_analysis' in daily_costs:
                console.print(f"   Budget usage: {daily_costs['cost_analysis']['budget_usage_percent']:.1f}%")
                console.print(f"   Within budget: {daily_costs['cost_analysis']['is_within_budget']}")
                
        # Test cost alerts
        console.print("\n🚨 Testing cost alerts...")
        alerts = billing_service.get_cost_alerts()
        
        if alerts and "error" not in alerts[0]:
            console.print(f"✅ {len(alerts)} cost alerts generated")
            for alert in alerts:
                level_color = "red" if alert["level"] == "critical" else "yellow" if alert["level"] == "warning" else "blue"
                console.print(f"   [{alert['level'].upper()}] {alert['message']}")
        else:
            console.print("ℹ️  No cost alerts generated")
            
        # Test billing export setup
        console.print("\n📤 Testing billing export setup...")
        export_status = billing_service.setup_billing_export()
        
        if "error" in export_status:
            console.print(f"❌ Error checking billing export: {export_status['error']}")
        else:
            if export_status['status'] == 'already_configured':
                console.print("✅ Billing export already configured")
            else:
                console.print("ℹ️  Billing export not configured")
                console.print("💡 Setup instructions:")
                for instruction in export_status.get('setup_instructions', []):
                    console.print(f"   {instruction}")
                    
        # Display billing dashboard
        console.print("\n📊 Billing Dashboard")
        console.print("=" * 60)
        billing_service.display_billing_dashboard()
        
        console.print("\n✅ Billing API integration test completed!")
        console.print("\n📝 Summary:")
        console.print("   - Billing account access: {'✅' if billing_account else '❌'}")
        console.print("   - BigQuery cost estimation: {'✅' if 'error' not in costs else '❌'}")
        console.print("   - Daily cost breakdown: {'✅' if 'error' not in daily_costs else '❌'}")
        console.print("   - Cost alerts: {'✅' if alerts and 'error' not in alerts[0] else '❌'}")
        
    except Exception as e:
        console.print(f"❌ Error testing billing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_billing_api()
