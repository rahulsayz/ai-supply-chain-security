#!/usr/bin/env python3
"""
Main execution script for Unified BigQuery AI processing
Updated to use the unified AI processor for cleaner integration
"""
import os
import sys
import click
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, validate_config, print_config_summary
from cost_monitor import get_cost_monitor
from billing_service import get_billing_service
from query_cost_tracker import get_query_cost_tracker
from budget_enforcer import get_budget_enforcer, BudgetRule, EnforcementLevel, EnforcementAction
from cost_history import get_cost_history, TimeGranularity

console = Console()

@click.group()
def cli():
    """Unified BigQuery AI Processing CLI for Supply Chain Security"""
    pass

@cli.command()
def setup():
    """Setup BigQuery AI environment and demo tables using unified processor"""
    console.print("\n🔧 Setting up BigQuery AI environment with Unified Processor...")
    
    if not validate_config():
        console.print("❌ Configuration validation failed. Please check your environment variables.")
        return
        
    print_config_summary()
    
    try:
        # Import and initialize unified processor
        console.print("\n🚀 Initializing Unified AI Processor...")
        from unified_ai_processor import UnifiedAIProcessor
        unified_processor = UnifiedAIProcessor()
        
        # Setup demo tables
        console.print("📊 Setting up demo tables...")
        unified_processor.setup_demo_tables()
        
        # Initialize budget enforcer
        console.print("🚨 Initializing budget enforcer...")
        budget_enforcer = get_budget_enforcer()
        
        console.print("\n✅ BigQuery AI environment setup completed successfully with Unified Processor!")
        
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        return

@cli.command()
def status():
    """Show current system status and cost information"""
    console.print("\n📊 BigQuery AI System Status (Unified Processor)")
    console.print("=" * 60)
    
    try:
        # Get cost monitor status
        cost_monitor = get_cost_monitor()
        cost_summary = cost_monitor.get_cost_summary()
        
        # Display cost overview
        cost_text = Text()
        cost_text.append(f"Today's Cost: ${cost_summary['today']['cost_usd']:.4f}\n", style="bold blue")
        cost_text.append(f"Budget Limit: ${cost_summary['today']['budget_limit_usd']:.2f}\n", style="bold green")
        cost_text.append(f"Remaining: ${cost_summary['today']['remaining_usd']:.4f}\n", style="bold yellow")
        cost_text.append(f"Usage: {cost_summary['today']['usage_percent']:.1f}%", 
                        style="bold red" if cost_summary['today']['usage_percent'] > 80 else "bold green")
        
        cost_panel = Panel(cost_text, title="💰 Cost Overview", border_style="blue")
        console.print(cost_panel)
        
        # Get unified processor status
        try:
            from unified_ai_processor import UnifiedAIProcessor
            unified_processor = UnifiedAIProcessor()
            
            # Display unified processor status
            status_table = Table(title="🔧 Unified Processor Status")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="green")
            status_table.add_column("Features", style="yellow")
            
            status_table.add_row("AI SQL Functions", "✅ Available", "6 functions")
            status_table.add_row("Vector Processing", "✅ Available", "4 functions")
            status_table.add_row("Multimodal Analysis", "✅ Available", "2 functions")
            status_table.add_row("Comprehensive Pipeline", "✅ Available", "5 phases")
            
            console.print(status_table)
            
        except Exception as e:
            console.print(f"⚠️ Unified processor status unavailable: {e}")
        
        # Display billing service status
        billing_status = cost_monitor.get_billing_status()
        if "error" not in billing_status:
            billing_text = Text()
            billing_text.append(f"Billing Account: {billing_status.get('billing_account', 'Not configured')}\n", style="bold blue")
            billing_text.append(f"Real-time Available: {'Yes' if billing_status.get('real_time_available') else 'No'}\n", style="bold green")
            billing_text.append(f"Cost Tracking: {billing_status.get('cost_tracking_method', 'Unknown')}\n", style="bold yellow")
            
            if 'billing_export' in billing_status:
                export_status = billing_status['billing_export']
                if export_status.get('status') == 'already_configured':
                    billing_text.append("Billing Export: ✅ Configured\n", style="bold green")
                else:
                    billing_text.append("Billing Export: ❌ Not configured\n", style="bold red")
                    
            billing_panel = Panel(billing_text, title="🏦 Billing Service Status", border_style="green")
            console.print(billing_panel)
            
        # Display query tracking status
        query_tracking_status = cost_monitor.get_query_tracking_status()
        if "error" not in query_tracking_status:
            query_text = Text()
            query_text.append(f"Query Tracking: {'✅ Enabled' if query_tracking_status.get('query_tracking_enabled') else '❌ Disabled'}\n", style="bold blue")
            query_text.append(f"Total Tracked Queries: {query_tracking_status.get('total_tracked_queries', 0)}\n", style="bold green")
            query_text.append(f"Tracked Cost: ${query_tracking_status.get('tracked_cost_usd', 0):.4f}\n", style="bold yellow")
            query_text.append(f"Cost Accuracy: {query_tracking_status.get('cost_accuracy_percent', 0):.1f}%", style="bold magenta")
            
            query_panel = Panel(query_text, title="🔍 Query Cost Tracking Status", border_style="cyan")
            console.print(query_panel)
            
        # Display budget enforcement status
        budget_enforcement_status = cost_monitor.get_budget_enforcement_status()
        if "error" not in budget_enforcement_status:
            budget_text = Text()
            budget_text.append(f"Budget Enforcement: {'✅ Enabled' if budget_enforcement_status.get('budget_enforcement_enabled') else '❌ Disabled'}\n", style="bold blue")
            budget_text.append(f"Active Rules: {budget_enforcement_status.get('active_rules', 0)}/{budget_enforcement_status.get('total_rules', 0)}\n", style="bold green")
            budget_text.append(f"Overall Status: {budget_enforcement_status.get('overall_status', 'Unknown')}\n", style="bold yellow")
            
            if 'enforcement_summary' in budget_enforcement_status:
                enforcement = budget_enforcement_status['enforcement_summary']
                if "error" not in enforcement:
                    budget_text.append(f"Total Violations: {enforcement.get('total_violations', 0)}\n", style="bold magenta")
                    budget_text.append(f"Resolution Rate: {enforcement.get('resolution_rate_percent', 0):.1f}%", style="bold cyan")
                    
            budget_panel = Panel(budget_text, title="🚨 Budget Enforcement Status", border_style="red")
            console.print(budget_panel)
            
        # Display cost history status
        cost_history_status = cost_monitor.get_cost_history_status()
        if "error" not in cost_history_status:
            history_text = Text()
            history_text.append(f"Cost History: {'✅ Enabled' if cost_history_status.get('cost_history_enabled') else '❌ Disabled'}\n", style="bold blue")
            history_text.append(f"Total Records: {cost_history_status.get('total_history_records', 0):,}\n", style="bold green")
            history_text.append(f"Trends Analyzed: {cost_history_status.get('trends_analyzed', 0)}\n", style="bold yellow")
            history_text.append(f"Anomalies Detected: {cost_history_status.get('anomalies_detected', 0)}", style="bold magenta")
            
            history_panel = Panel(history_text, title="📊 Cost History Status", border_style="cyan")
            console.print(history_panel)
        
    except Exception as e:
        console.print(f"❌ Error getting status: {e}")

@cli.command()
def demo():
    """Run comprehensive demo using unified processor"""
    console.print("\n🎯 Running Comprehensive Demo with Unified Processor")
    console.print("=" * 70)
    
    try:
        from unified_ai_processor import UnifiedAIProcessor
        unified_processor = UnifiedAIProcessor()
        
        console.print("🚀 Starting comprehensive supply chain analysis demo...")
        results = unified_processor.run_demo()
        
        if results.get("success"):
            console.print("\n✅ Demo completed successfully!")
            console.print(f"📊 Analysis completed in {results.get('processing_time', 0):.2f} seconds")
            
            # Display results summary
            if 'summary' in results:
                summary = results['summary']
                console.print(f"\n📈 Demo Summary:")
                console.print(f"  - AI SQL Analysis: {summary.get('ai_sql_analysis', {}).get('status', 'Unknown')}")
                console.print(f"  - Vector Analysis: {summary.get('vector_analysis', {}).get('status', 'Unknown')}")
                console.print(f"  - Multimodal Analysis: {summary.get('multimodal_analysis', {}).get('status', 'Unknown')}")
                console.print(f"  - Cross-Analysis: {summary.get('cross_analysis', {}).get('status', 'Unknown')}")
                console.print(f"  - Report Generation: {summary.get('report_generation', {}).get('status', 'Unknown')}")
        else:
            console.print(f"❌ Demo failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        console.print(f"❌ Demo failed: {e}")

@cli.command()
@click.option('--threat-id', default=None, help='Specific threat report ID to analyze')
@click.option('--query', default=None, help='Natural language query for analysis')
@click.option('--assets', default=None, help='Comma-separated list of asset IDs to analyze')
def analyze(threat_id, query, assets):
    """Run comprehensive supply chain analysis using unified processor"""
    console.print("\n🔍 Running Comprehensive Supply Chain Analysis")
    console.print("=" * 60)
    
    try:
        from unified_ai_processor import UnifiedAIProcessor
        unified_processor = UnifiedAIProcessor()
        
        # Parse asset IDs
        asset_ids = None
        if assets:
            asset_ids = [asset.strip() for asset in assets.split(',')]
        
        console.print(f"🎯 Analysis Parameters:")
        console.print(f"  - Threat ID: {threat_id or 'Not specified'}")
        console.print(f"  - Query: {query or 'Not specified'}")
        console.print(f"  - Asset IDs: {asset_ids or 'Not specified'}")
        
        console.print("\n🚀 Starting comprehensive analysis...")
        results = unified_processor.run_comprehensive_supply_chain_analysis(
            threat_report_id=threat_id,
            query_text=query,
            asset_ids=asset_ids
        )
        
        if results.get("success"):
            console.print("\n✅ Analysis completed successfully!")
            console.print(f"📊 Processing time: {results.get('processing_time', 0):.2f} seconds")
            
            # Display results summary
            if 'summary' in results:
                summary = results['summary']
                console.print(f"\n📈 Analysis Summary:")
                console.print(f"  - Overall Risk Score: {summary.get('overall_risk_score', 'Unknown')}")
                console.print(f"  - Threat Count: {summary.get('threat_count', 0)}")
                console.print(f"  - Vendor Count: {summary.get('vendor_count', 0)}")
                console.print(f"  - Asset Count: {summary.get('asset_count', 0)}")
                
                if 'recommendations' in summary:
                    recs = summary['recommendations']
                    console.print(f"\n💡 Key Recommendations:")
                    for i, rec in enumerate(recs[:5], 1):  # Show top 5
                        console.print(f"  {i}. {rec}")
        else:
            console.print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        console.print(f"❌ Analysis failed: {e}")

@cli.command()
def test():
    """Run comprehensive test suite using simplified processor"""
    console.print("\n🧪 Running Comprehensive Test Suite")
    console.print("=" * 50)
    
    try:
        from unified_ai_processor_simple import UnifiedAIProcessorSimple
        processor = UnifiedAIProcessorSimple()
        
        results = processor.run_comprehensive_test()
        
        if results.get("success"):
            console.print("\n✅ All tests passed!")
        else:
            console.print(f"\n❌ Some tests failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        console.print(f"❌ Test suite failed: {e}")

@cli.command()
def billing():
    """Test BigQuery Billing API integration"""
    console.print("\n🏦 Testing BigQuery Billing API Integration")
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
            console.print("💡 Make sure your service account has billing access")
            return
            
        # Test real-time cost retrieval
        console.print("\n💰 Testing real-time cost retrieval...")
        costs = billing_service.get_real_time_costs(days=7)
        
        if "error" in costs:
            console.print(f"❌ Error getting costs: {costs['error']}")
        else:
            console.print(f"✅ Retrieved costs for {len(costs)} days")
            try:
                total_cost = sum(day['cost_usd'] for day in costs.values())
                console.print(f"💰 Total cost over 7 days: ${total_cost:.4f}")
            except (KeyError, TypeError):
                console.print("💰 Cost data retrieved but format may vary")
            
    except Exception as e:
        console.print(f"❌ Billing test failed: {e}")

@cli.command()
def costs():
    """Show detailed cost information and trends"""
    console.print("\n💰 Detailed Cost Information and Trends")
    console.print("=" * 50)
    
    try:
        cost_monitor = get_cost_monitor()
        
        # Get cost summary
        cost_summary = cost_monitor.get_cost_summary()
        
        # Display daily costs
        try:
            from datetime import datetime, timedelta
            daily_costs = {}
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                daily_cost = cost_monitor.get_daily_cost(date)
                daily_costs[date] = {'cost_usd': daily_cost, 'usage_percent': (daily_cost / 5.0) * 100}
            
            if daily_costs:
                cost_table = Table(title="📊 Daily Costs (Last 7 Days)")
                cost_table.add_column("Date", style="cyan")
                cost_table.add_column("Cost (USD)", style="green")
                cost_table.add_column("Budget Used", style="yellow")
                
                for date, cost_data in daily_costs.items():
                    cost_table.add_row(
                        date,
                        f"${cost_data['cost_usd']:.4f}",
                        f"{cost_data['usage_percent']:.1f}%"
                    )
                
                console.print(cost_table)
        except Exception as e:
            console.print(f"⚠️ Daily costs display unavailable: {e}")
        
        # Get cost trends
        try:
            from cost_history import get_cost_history
            cost_history = get_cost_history()
            cost_trends = cost_history.analyze_cost_trends(days=30)
            
            if cost_trends:
                trends_text = Text()
                trends_text.append(f"Trends Analyzed: {len(cost_trends)}\n", style="bold blue")
                
                # Show most recent trend
                if cost_trends:
                    latest_trend = cost_trends[0]
                    trends_text.append(f"Latest Trend: {getattr(latest_trend, 'trend_type', 'Unknown')}\n", style="bold green")
                    trends_text.append(f"Trend Period: {getattr(latest_trend, 'period_days', 0)} days\n", style="bold yellow")
                
                trends_panel = Panel(trends_text, title="📈 Cost Trends", border_style="cyan")
                console.print(trends_panel)
        except Exception as e:
            console.print(f"⚠️ Cost trends unavailable: {e}")
        
        # Get anomalies
        try:
            from cost_history import get_cost_history
            cost_history = get_cost_history()
            anomalies = cost_history.detect_cost_anomalies(days=30)
            
            if anomalies:
                anomaly_text = Text()
                for anomaly in anomalies[:5]:  # Show top 5
                    anomaly_text.append(f"• {anomaly.get('date', 'Unknown')}: ${anomaly.get('cost_usd', 0):.4f} "
                                     f"({anomaly.get('severity', 'unknown')} severity)\n", 
                                     style="bold red" if anomaly.get('severity') == 'high' else "bold yellow")
                
                anomaly_panel = Panel(anomaly_text, title="🚨 Cost Anomalies", border_style="red")
                console.print(anomaly_panel)
            else:
                console.print("✅ No cost anomalies detected")
        except Exception as e:
            console.print(f"⚠️ Cost anomalies unavailable: {e}")
        
    except Exception as e:
        console.print(f"❌ Error getting cost information: {e}")

@cli.command()
def export():
    """Export data and analysis results"""
    console.print("\n📁 Exporting Data and Analysis Results")
    console.print("=" * 50)
    
    try:
        from unified_ai_processor import UnifiedAIProcessor
        unified_processor = UnifiedAIProcessor()
        
        # Export threat data
        console.print("📊 Exporting threat data...")
        threat_export = unified_processor.export_data("threats")
        
        if threat_export.get("success"):
            console.print(f"✅ Exported {threat_export.get('record_count', 0)} threat records")
        else:
            console.print(f"❌ Threat export failed: {threat_export.get('error', 'Unknown error')}")
        
        # Export vendor data
        console.print("🏢 Exporting vendor data...")
        vendor_export = unified_processor.export_data("vendors")
        
        if vendor_export.get("success"):
            console.print(f"✅ Exported {vendor_export.get('record_count', 0)} vendor records")
        else:
            console.print(f"❌ Vendor export failed: {vendor_export.get('error', 'Unknown error')}")
        
        # Export analytics data
        console.print("📈 Exporting analytics data...")
        analytics_export = unified_processor.export_data("analytics")
        
        if analytics_export.get("success"):
            console.print(f"✅ Exported {analytics_export.get('record_count', 0)} analytics records")
        else:
            console.print(f"❌ Analytics export failed: {analytics_export.get('error', 'Unknown error')}")
            
    except Exception as e:
        console.print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    cli()
