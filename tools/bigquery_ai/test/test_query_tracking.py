#!/usr/bin/env python3
"""
Test script for Query Cost Tracking functionality
"""
import os
import sys
import time
from datetime import datetime
import json

# Set the correct project ID for testing
os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_cost_tracker import get_query_cost_tracker
from rich.console import Console

console = Console()

def test_query_cost_tracking():
    """Test the query cost tracking functionality"""
    console.print("🔍 Testing Query Cost Tracking Functionality")
    console.print("=" * 60)
    
    try:
        query_tracker = get_query_cost_tracker()
        
        # Test 1: Basic functionality
        console.print("\n🧪 Test 1: Basic Query Cost Tracking")
        console.print("=" * 40)
        
        # Simulate some test queries
        test_queries = [
            {
                "query": "SELECT * FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` LIMIT 10",
                "type": "test_query",
                "execution_time": 1500
            },
            {
                "query": "SELECT COUNT(*) FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports`",
                "type": "count_query",
                "execution_time": 800
            },
            {
                "query": "SELECT vendor_name, COUNT(*) as threat_count FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` GROUP BY vendor_name",
                "type": "aggregation_query",
                "execution_time": 2200
            }
        ]
        
        # Track each test query
        for i, test_query in enumerate(test_queries, 1):
            console.print(f"   Tracking query {i}: {test_query['type']}")
            
            record = query_tracker.track_query_execution(
                query=test_query["query"],
                query_type=test_query["type"],
                execution_time_ms=test_query["execution_time"]
            )
            
            if record:
                console.print(f"     ✅ Tracked: ${record.actual_cost_usd:.4f} ({record.priority} priority)")
            else:
                console.print(f"     ❌ Failed to track")
                
        # Test 2: Cost Summary
        console.print("\n🧪 Test 2: Query Cost Summary")
        console.print("=" * 40)
        
        summary = query_tracker.get_query_cost_summary(days=1)
        if "error" in summary:
            console.print(f"❌ Error: {summary['error']}")
        else:
            console.print("✅ Cost summary generated successfully")
            console.print(f"   Total queries: {summary['total_queries']}")
            console.print(f"   Total cost: ${summary['total_cost_usd']:.4f}")
            console.print(f"   Cost accuracy: {summary['cost_accuracy_percent']:.1f}%")
            console.print(f"   Avg execution time: {summary['avg_execution_time_ms']:.0f}ms")
            
        # Test 3: Performance Metrics
        console.print("\n🧪 Test 3: Performance Metrics")
        console.print("=" * 40)
        
        performance = query_tracker.get_query_performance_metrics(days=1)
        if "error" in performance:
            console.print(f"❌ Error: {performance['error']}")
        else:
            console.print("✅ Performance metrics generated successfully")
            console.print(f"   Total queries: {performance['total_queries']}")
            console.print(f"   Avg execution time: {performance['avg_execution_time_ms']:.0f}ms")
            console.print(f"   Avg cost: ${performance['avg_cost_usd']:.4f}")
            console.print(f"   Outliers: {performance['outliers_count']}")
            
        # Test 4: Expensive Queries
        console.print("\n🧪 Test 4: Expensive Queries Analysis")
        console.print("=" * 40)
        
        expensive_queries = query_tracker.get_expensive_queries(limit=5, days=1)
        if expensive_queries:
            console.print(f"✅ Found {len(expensive_queries)} expensive queries")
            for i, record in enumerate(expensive_queries, 1):
                console.print(f"   {i}. {record.query_type}: ${record.actual_cost_usd:.4f} ({record.priority})")
        else:
            console.print("ℹ️  No expensive queries found")
            
        # Test 5: Cost Trends
        console.print("\n🧪 Test 5: Cost Trends Analysis")
        console.print("=" * 40)
        
        if 'cost_trends' in summary and 'error' not in summary['cost_trends']:
            trends = summary['cost_trends']
            console.print("✅ Cost trends calculated successfully")
            console.print(f"   Trend: {trends['trend']}")
            console.print(f"   Cost change: {trends['cost_change_percent']:+.1f}%")
            console.print(f"   Date range: {trends['date_range']['start']} to {trends['date_range']['end']}")
        else:
            console.print("ℹ️  No cost trends available (insufficient data)")
            
        # Test 6: Dashboard Display
        console.print("\n🧪 Test 6: Dashboard Display")
        console.print("=" * 40)
        
        console.print("Displaying query cost dashboard...")
        query_tracker.display_query_cost_dashboard(days=1)
        
        # Test 7: Data Persistence
        console.print("\n🧪 Test 7: Data Persistence")
        console.print("=" * 40)
        
        # Check if data was saved
        if os.path.exists("query_cost_history.json"):
            console.print("✅ Query cost history file created")
            with open("query_cost_history.json", 'r') as f:
                data = json.load(f)
                console.print(f"   Records saved: {len(data)}")
        else:
            console.print("❌ Query cost history file not found")
            
        console.print("\n✅ Query Cost Tracking Test Completed!")
        
        # Display final summary
        console.print("\n📊 Final Summary")
        console.print("=" * 40)
        final_summary = query_tracker.get_query_cost_summary(days=1)
        if "error" not in final_summary:
            console.print(f"   Total queries tracked: {final_summary['total_queries']}")
            console.print(f"   Total cost tracked: ${final_summary['total_cost_usd']:.4f}")
            console.print(f"   Cost accuracy: {final_summary['cost_accuracy_percent']:.1f}%")
            console.print(f"   Query types: {list(final_summary.get('cost_by_type', {}).keys())}")
            
    except Exception as e:
        console.print(f"❌ Error testing query cost tracking: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_cost_tracking()
