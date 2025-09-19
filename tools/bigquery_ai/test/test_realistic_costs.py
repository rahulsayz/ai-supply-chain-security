#!/usr/bin/env python3
"""
Test script for realistic query cost tracking scenarios
"""
import os
import sys
import time
from datetime import datetime

# Set the correct project ID for testing
os.environ['GCP_PROJECT_ID'] = 'ai-sales-agent-452915'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_cost_tracker import get_query_cost_tracker
from rich.console import Console

console = Console()

def test_realistic_cost_scenarios():
    """Test query cost tracking with realistic cost scenarios"""
    console.print("💰 Testing Realistic Query Cost Scenarios")
    console.print("=" * 60)
    
    try:
        query_tracker = get_query_cost_tracker()
        
        # Clear existing test data
        console.print("🧹 Clearing existing test data...")
        query_tracker.cost_records = []
        query_tracker.save_cost_history()
        
        # Simulate realistic query scenarios with different costs
        realistic_scenarios = [
            {
                "query": "SELECT * FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` WHERE severity = 'HIGH'",
                "type": "threat_analysis",
                "execution_time": 2500,
                "simulated_cost": 0.15
            },
            {
                "query": "SELECT vendor_name, COUNT(*) as threat_count, AVG(severity_score) as avg_severity FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` GROUP BY vendor_name ORDER BY threat_count DESC",
                "type": "vendor_risk_assessment",
                "execution_time": 4200,
                "simulated_cost": 0.45
            },
            {
                "query": "SELECT * FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` WHERE threat_type IN ('malware', 'phishing', 'ransomware') AND detection_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)",
                "type": "malware_analysis",
                "execution_time": 3800,
                "simulated_cost": 0.32
            },
            {
                "query": "SELECT threat_id, description, severity, vendor_name, detection_date FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` WHERE severity_score > 8.0 ORDER BY detection_date DESC LIMIT 100",
                "type": "critical_threats",
                "execution_time": 1800,
                "simulated_cost": 0.08
            },
            {
                "query": "SELECT DATE(detection_date) as date, COUNT(*) as daily_threats, AVG(severity_score) as avg_severity FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` WHERE detection_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) GROUP BY DATE(detection_date) ORDER BY date",
                "type": "trend_analysis",
                "execution_time": 3200,
                "simulated_cost": 0.28
            },
            {
                "query": "SELECT vendor_name, threat_type, COUNT(*) as count FROM `ai-sales-agent-452915.supply_chain_ai.demo_threat_reports` GROUP BY vendor_name, threat_type HAVING count > 5 ORDER BY count DESC",
                "type": "pattern_analysis",
                "execution_time": 5500,
                "simulated_cost": 0.65
            }
        ]
        
        # Track each realistic scenario
        console.print("\n🧪 Simulating Realistic Query Scenarios")
        console.print("=" * 50)
        
        for i, scenario in enumerate(realistic_scenarios, 1):
            console.print(f"   Scenario {i}: {scenario['type']}")
            
            # Create a mock job object with simulated costs
            class MockJob:
                def __init__(self, cost, execution_time):
                    self.total_bytes_processed = int(cost * 1000000000)  # Simulate bytes based on cost
                    self.total_slot_ms = execution_time * 1000  # Convert to milliseconds
                    
            mock_job = MockJob(scenario['simulated_cost'], scenario['execution_time'])
            
            record = query_tracker.track_query_execution(
                query=scenario["query"],
                query_type=scenario["type"],
                job=mock_job,
                execution_time_ms=scenario["execution_time"]
            )
            
            if record:
                priority_color = "red" if record.priority == "critical" else "yellow" if record.priority == "high" else "green"
                console.print(f"     ✅ Tracked: ${record.actual_cost_usd:.4f} ([bold {priority_color}]{record.priority}[/bold {priority_color}] priority)")
            else:
                console.print(f"     ❌ Failed to track")
                
        # Test comprehensive analytics
        console.print("\n📊 Testing Comprehensive Analytics")
        console.print("=" * 50)
        
        # Get summary for different time periods
        for days in [1, 7, 30]:
            summary = query_tracker.get_query_cost_summary(days=days)
            if "error" not in summary:
                console.print(f"   {days} day summary:")
                console.print(f"     Total queries: {summary['total_queries']}")
                console.print(f"     Total cost: ${summary['total_cost_usd']:.4f}")
                console.print(f"     Cost accuracy: {summary['cost_accuracy_percent']:.1f}%")
                console.print(f"     Avg cost/query: ${summary['avg_cost_per_query']:.4f}")
                
        # Test performance metrics
        console.print("\n⚡ Performance Analysis")
        console.print("=" * 40)
        
        performance = query_tracker.get_query_performance_metrics(days=1)
        if "error" not in performance:
            console.print(f"   Total queries: {performance['total_queries']}")
            console.print(f"   Avg execution time: {performance['avg_execution_time_ms']:.0f}ms")
            console.print(f"   Avg cost: ${performance['avg_cost_usd']:.4f}")
            console.print(f"   Outliers: {performance['outliers_count']}")
            
            # Show distribution breakdowns
            if 'performance_distribution' in performance:
                console.print("   Performance distribution:")
                for category, count in performance['performance_distribution'].items():
                    percentage = (count / performance['total_queries'] * 100) if performance['total_queries'] > 0 else 0
                    console.print(f"     {category.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
                    
        # Test expensive queries analysis
        console.print("\n💸 Expensive Queries Analysis")
        console.print("=" * 40)
        
        expensive_queries = query_tracker.get_expensive_queries(limit=10, days=1)
        if expensive_queries:
            console.print(f"   Top {len(expensive_queries)} most expensive queries:")
            for i, record in enumerate(expensive_queries, 1):
                priority_color = "red" if record.priority == "critical" else "yellow" if record.priority == "high" else "green"
                console.print(f"     {i}. {record.query_type}: ${record.actual_cost_usd:.4f} ({record.execution_time_ms}ms) - [bold {priority_color}]{record.priority}[/bold {priority_color}]")
                
        # Test cost trends
        console.print("\n📈 Cost Trends Analysis")
        console.print("=" * 40)
        
        summary = query_tracker.get_query_cost_summary(days=1)
        if 'cost_trends' in summary and 'error' not in summary['cost_trends']:
            trends = summary['cost_trends']
            console.print(f"   Overall trend: {trends['trend']}")
            console.print(f"   Cost change: {trends['cost_change_percent']:+.1f}%")
            console.print(f"   Date range: {trends['date_range']['start']} to {trends['date_range']['end']}")
            
            # Show daily breakdown
            if 'daily_costs' in trends:
                console.print("   Daily cost breakdown:")
                for date, data in trends['daily_costs'].items():
                    console.print(f"     {date}: ${data['cost']:.4f} ({data['count']} queries)")
                    
        # Test priority analysis
        console.print("\n🚨 Priority Analysis")
        console.print("=" * 40)
        
        if 'priority_breakdown' in summary:
            for priority, data in summary['priority_breakdown'].items():
                priority_color = "red" if priority == "critical" else "yellow" if priority == "high" else "green"
                console.print(f"   [bold {priority_color}]{priority.upper()}[/bold {priority_color}]: {data['count']} queries, ${data['total_cost']:.4f}")
                
        # Test query type analysis
        console.print("\n🔍 Query Type Analysis")
        console.print("=" * 40)
        
        if 'cost_by_type' in summary:
            for query_type, data in summary['cost_by_type'].items():
                cost_percentage = (data['total_cost'] / summary['total_cost_usd'] * 100) if summary['total_cost_usd'] > 0 else 0
                console.print(f"   {query_type}: {data['count']} queries, ${data['total_cost']:.4f} ({cost_percentage:.1f}%)")
                
        # Display comprehensive dashboard
        console.print("\n📊 Comprehensive Query Cost Dashboard")
        console.print("=" * 60)
        query_tracker.display_query_cost_dashboard(days=1)
        
        console.print("\n✅ Realistic Cost Scenarios Test Completed!")
        
        # Final summary
        console.print("\n📊 Final Summary")
        console.print("=" * 40)
        final_summary = query_tracker.get_query_cost_summary(days=1)
        if "error" not in final_summary:
            console.print(f"   Total queries tracked: {final_summary['total_queries']}")
            console.print(f"   Total cost tracked: ${final_summary['total_cost_usd']:.4f}")
            console.print(f"   Cost accuracy: {final_summary['cost_accuracy_percent']:.1f}%")
            console.print(f"   Query types: {list(final_summary.get('cost_by_type', {}).keys())}")
            console.print(f"   Priority levels: {list(final_summary.get('priority_breakdown', {}).keys())}")
            
    except Exception as e:
        console.print(f"❌ Error testing realistic cost scenarios: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_realistic_cost_scenarios()
