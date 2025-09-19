#!/usr/bin/env python3
"""
Test script for enhanced cost monitor with billing service integration
"""
import os
import sys
from datetime import datetime

# Set the correct project ID for testing
os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_monitor import get_cost_monitor
from rich.console import Console

console = Console()

def test_cost_monitor():
    """Test the enhanced cost monitor with billing service integration"""
    console.print("💰 Testing Enhanced Cost Monitor with Billing Service")
    console.print("=" * 60)
    
    try:
        cost_monitor = get_cost_monitor()
        
        # Test cost summary
        console.print("📊 Testing cost summary...")
        summary = cost_monitor.get_cost_summary()
        
        if summary:
            console.print("✅ Cost summary retrieved successfully")
            console.print(f"   Today's cost: ${summary['today']['cost_usd']:.4f}")
            console.print(f"   Budget limit: ${summary['today']['budget_limit_usd']:.2f}")
            console.print(f"   Remaining: ${summary['today']['remaining_usd']:.4f}")
            console.print(f"   Usage: {summary['today']['usage_percent']:.1f}%")
            
            # Check if real-time billing data is available
            if 'real_time_billing' in summary:
                console.print("   Real-time billing: ✅ Available")
                real_time = summary['real_time_billing']
                console.print(f"     Billing account: {real_time.get('billing_account', 'N/A')}")
                console.print(f"     BigQuery costs: ${real_time.get('bigquery_costs', {}).get('total_cost', 0):.4f}")
            else:
                console.print("   Real-time billing: ❌ Not available")
        else:
            console.print("❌ Failed to get cost summary")
            
        # Test billing status
        console.print("\n🏦 Testing billing status...")
        billing_status = cost_monitor.get_billing_status()
        
        if "error" not in billing_status:
            console.print("✅ Billing status retrieved successfully")
            console.print(f"   Billing account: {billing_status.get('billing_account', 'Not configured')}")
            console.print(f"   Real-time available: {'Yes' if billing_status.get('real_time_available') else 'No'}")
            console.print(f"   Cost tracking method: {billing_status.get('cost_tracking_method', 'Unknown')}")
            
            if 'billing_export' in billing_status:
                export_status = billing_status['billing_export']
                if export_status.get('status') == 'already_configured':
                    console.print("   Billing export: ✅ Configured")
                else:
                    console.print("   Billing export: ❌ Not configured")
        else:
            console.print(f"❌ Error getting billing status: {billing_status['error']}")
            
        # Test cost alerts
        console.print("\n🚨 Testing cost alerts...")
        try:
            alerts = cost_monitor.billing_service.get_cost_alerts()
            if alerts and "error" not in alerts[0]:
                console.print(f"✅ {len(alerts)} cost alerts generated")
                for alert in alerts:
                    level_color = "red" if alert["level"] == "critical" else "yellow" if alert["level"] == "warning" else "blue"
                    console.print(f"   [{alert['level'].upper()}] {alert['message']}")
            else:
                console.print("ℹ️  No cost alerts generated")
        except Exception as e:
            console.print(f"⚠️  Could not get cost alerts: {e}")
            
        # Test budget enforcement
        console.print("\n💳 Testing budget enforcement...")
        test_costs = [0.1, 1.0, 5.0, 10.0]  # Test different cost scenarios
        
        for test_cost in test_costs:
            can_execute, message = cost_monitor.can_execute_query(test_cost)
            status_icon = "✅" if can_execute else "❌"
            console.print(f"   ${test_cost:.2f} query: {status_icon} {message}")
            
        # Display enhanced cost dashboard
        console.print("\n📊 Enhanced Cost Dashboard")
        console.print("=" * 60)
        cost_monitor.display_cost_dashboard()
        
        console.print("\n✅ Enhanced cost monitor test completed!")
        
    except Exception as e:
        console.print(f"❌ Error testing cost monitor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cost_monitor()
