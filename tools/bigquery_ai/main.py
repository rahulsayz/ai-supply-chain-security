#!/usr/bin/env python3
"""
Main execution script for BigQuery AI processing
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
from ai_processor import get_ai_processor
from vector_processor import get_vector_processor
from multimodal_processor import get_multimodal_processor
from data_export import get_data_exporter

console = Console()

@click.group()
def cli():
    """BigQuery AI Processing CLI for Supply Chain Security"""
    pass

@cli.command()
def setup():
    """Setup BigQuery AI environment and demo tables"""
    console.print("\n🔧 Setting up BigQuery AI environment...")
    
    if not validate_config():
        console.print("❌ Configuration validation failed. Please check your environment variables.")
        return
        
    print_config_summary()
    
    try:
        # Initialize AI processor (creates demo tables)
        console.print("\n📊 Initializing AI processor...")
        ai_processor = get_ai_processor()
        
        # Initialize vector processor
        console.print("🔍 Initializing vector processor...")
        vector_processor = get_vector_processor()
        
        # Initialize multimodal processor
        console.print("🏗️ Initializing multimodal processor...")
        multimodal_processor = get_multimodal_processor()
        
        # Initialize data exporter
        console.print("📁 Initializing data exporter...")
        data_exporter = get_data_exporter()
        
        # Initialize budget enforcer
        console.print("🚨 Initializing budget enforcer...")
        budget_enforcer = get_budget_enforcer()
        
        console.print("\n✅ BigQuery AI environment setup completed successfully!")
        
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        return

@cli.command()
def status():
    """Show current system status and cost information"""
    console.print("\n📊 BigQuery AI System Status")
    console.print("=" * 50)
    
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
        
        # Get processor statuses
        ai_status = get_ai_processor().get_processing_status()
        vector_status = get_vector_processor().get_vector_search_status()
        multimodal_status = get_multimodal_processor().get_multimodal_status()
        
        # Display processor statuses
        status_table = Table(title="🔧 Processor Status")
        status_table.add_column("Processor", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Features", style="yellow")
        
        status_table.add_row("AI Processor", ai_status["status"], str(len(ai_status.get("config", {}))))
        status_table.add_row("Vector Processor", vector_status["status"], str(len(vector_status.get("features", {}))))
        status_table.add_row("Multimodal Processor", multimodal_status["status"], str(len(multimodal_status.get("features", {}))))
        
        console.print(status_table)
        
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
            console.print("✅ Real-time costs retrieved successfully")
            console.print(f"   BigQuery costs: ${costs['bigquery_costs'].get('total_cost', 0):.4f}")
            console.print(f"   Project costs: ${costs['project_costs'].get('total_cost', 0):.4f}")
            console.print(f"   Total: ${costs['total_costs']['overall']:.4f}")
            
        # Test daily cost breakdown
        console.print("\n📅 Testing daily cost breakdown...")
        daily_costs = billing_service.get_daily_cost_breakdown()
        
        if "error" in daily_costs:
            console.print(f"❌ Error getting daily costs: {daily_costs['error']}")
        else:
            console.print("✅ Daily cost breakdown retrieved")
            console.print(f"   Date: {daily_costs['date']}")
            console.print(f"   Total cost: ${daily_costs['total_cost']:.4f}")
            console.print(f"   Budget usage: {daily_costs['cost_analysis']['budget_usage_percent']:.1f}%")
            
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
        
    except Exception as e:
        console.print(f"❌ Error testing billing API: {e}")

@cli.command()
def budget_enforcement():
    """Display budget enforcement dashboard and status"""
    console.print("\n🚨 Budget Enforcement Dashboard")
    console.print("=" * 60)
    
    try:
        budget_enforcer = get_budget_enforcer()
        budget_enforcer.display_budget_dashboard()
        
    except Exception as e:
        console.print(f"❌ Error displaying budget enforcement dashboard: {e}")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
def budget_analytics(days):
    """Display budget enforcement analytics and violations"""
    console.print(f"\n📊 Budget Enforcement Analytics (Last {days} days)")
    console.print("=" * 60)
    
    try:
        budget_enforcer = get_budget_enforcer()
        
        # Get enforcement summary
        enforcement_summary = budget_enforcer.get_enforcement_summary(days=days)
        if "error" in enforcement_summary:
            console.print(f"❌ Error: {enforcement_summary['error']}")
            return
            
        # Overall enforcement status
        status_text = Text()
        status_text.append(f"Total Violations: {enforcement_summary['total_violations']}\n", style="bold blue")
        status_text.append(f"Resolved: {enforcement_summary['resolved_violations']}\n", style="bold green")
        status_text.append(f"Unresolved: {enforcement_summary['unresolved_violations']}\n", style="bold yellow")
        status_text.append(f"Resolution Rate: {enforcement_summary['resolution_rate_percent']:.1f}%\n", style="bold magenta")
        status_text.append(f"Active Rules: {enforcement_summary['active_rules']}/{enforcement_summary['total_rules']}", style="bold cyan")
        
        status_panel = Panel(status_text, title="📊 Enforcement Overview", border_style="blue")
        console.print(status_panel)
        
        # Violation counts by type
        if enforcement_summary['violation_counts']:
            violation_table = Table(title="🚨 Violations by Type")
            violation_table.add_column("Type", style="cyan")
            violation_table.add_column("Count", style="magenta")
            violation_table.add_column("Percentage", style="green")
            
            total_violations = enforcement_summary['total_violations']
            for violation_type, count in enforcement_summary['violation_counts'].items():
                percentage = (count / total_violations * 100) if total_violations > 0 else 0
                violation_table.add_row(
                    violation_type.replace('_', ' ').title(),
                    str(count),
                    f"{percentage:.1f}%"
                )
                
            console.print(violation_table)
            
        # Enforcement actions
        if enforcement_summary['action_counts']:
            action_table = Table(title="⚡ Enforcement Actions")
            action_table.add_column("Action", style="cyan")
            action_table.add_column("Count", style="magenta")
            action_table.add_column("Percentage", style="green")
            
            for action, count in enforcement_summary['action_counts'].items():
                percentage = (count / total_violations * 100) if total_violations > 0 else 0
                action_table.add_row(
                    action.replace('_', ' ').title(),
                    str(count),
                    f"{percentage:.1f}%"
                )
                
            console.print(action_table)
            
        # Recent violations
        recent_violations = budget_enforcer.get_budget_violations(days=days, resolved=False)
        if recent_violations:
            console.print(f"\n🚨 Recent Unresolved Violations (Last {days} days)")
            console.print("=" * 60)
            
            violations_table = Table(title="🚨 Unresolved Violations")
            violations_table.add_column("Time", style="cyan")
            violations_table.add_column("Rule", style="magenta")
            violations_table.add_column("Type", style="green")
            violations_table.add_column("Current", style="yellow")
            violations_table.add_column("Limit", style="blue")
            violations_table.add_column("Action", style="red")
            
            for violation in recent_violations[-10:]:  # Show last 10
                rule_name = next((r.name for r in budget_enforcer.budget_rules if r.rule_id == violation.rule_id), 'Unknown')
                time_str = violation.timestamp[:19]
                
                violations_table.add_row(
                    time_str,
                    rule_name,
                    violation.violation_type,
                    f"${violation.current_amount:.4f}",
                    f"${violation.limit_amount:.2f}",
                    violation.enforcement_action.value
                )
                
            console.print(violations_table)
        else:
            console.print(f"✅ No unresolved violations in the last {days} days")
            
    except Exception as e:
        console.print(f"❌ Error displaying budget analytics: {e}")

@cli.command()
@click.option('--rule-id', help='Rule ID to resolve')
def resolve_violation(rule_id):
    """Resolve a budget violation"""
    if not rule_id:
        console.print("❌ Please provide a rule ID to resolve")
        return
        
    try:
        budget_enforcer = get_budget_enforcer()
        budget_enforcer.resolve_violation(rule_id)
        console.print(f"✅ Budget violation {rule_id} resolved successfully")
        
    except Exception as e:
        console.print(f"❌ Error resolving violation: {e}")

@cli.command()
@click.option('--name', required=True, help='Rule name')
@click.option('--description', required=True, help='Rule description')
@click.option('--budget-type', required=True, type=click.Choice(['daily', 'weekly', 'monthly', 'per_query']), help='Budget type')
@click.option('--amount', required=True, type=float, help='Budget amount in USD')
@click.option('--enforcement-level', required=True, type=click.Choice(['monitoring', 'warning', 'throttling', 'blocking', 'emergency']), help='Enforcement level')
@click.option('--warning-threshold', default=80.0, type=float, help='Warning threshold percentage')
@click.option('--critical-threshold', default=95.0, type=float, help='Critical threshold percentage')
def add_budget_rule(name, description, budget_type, amount, enforcement_level, warning_threshold, critical_threshold):
    """Add a new budget rule"""
    try:
        budget_enforcer = get_budget_enforcer()
        
        # Create new rule
        rule = BudgetRule(
            rule_id="",  # Will be generated
            name=name,
            description=description,
            budget_type=budget_type,
            amount_usd=amount,
            enforcement_level=EnforcementLevel(enforcement_level),
            actions=[EnforcementAction.WARN, EnforcementAction.BLOCK],  # Default actions
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            enabled=True,
            created_at="",  # Will be generated
            updated_at=""   # Will be generated
        )
        
        budget_enforcer.add_budget_rule(rule)
        console.print(f"✅ Budget rule '{name}' added successfully")
        
    except Exception as e:
        console.print(f"❌ Error adding budget rule: {e}")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
def cost_history(days):
    """Display cost history dashboard and analytics"""
    console.print(f"\n📊 Cost History Dashboard (Last {days} days)")
    console.print("=" * 60)
    
    try:
        cost_history = get_cost_history()
        
        # Display comprehensive dashboard
        cost_history.display_cost_history_dashboard(days=days)
        
    except Exception as e:
        console.print(f"❌ Error displaying cost history dashboard: {e}")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
def cost_analytics(days):
    """Advanced cost analytics and trend analysis"""
    console.print(f"\n📈 Advanced Cost Analytics (Last {days} days)")
    console.print("=" * 60)
    
    try:
        cost_history = get_cost_history()
        
        # Analyze cost trends
        console.print("\n📈 Cost Trends Analysis")
        console.print("=" * 40)
        trends = cost_history.analyze_cost_trends(days=days)
        
        if trends:
            trend_table = Table(title="📊 Cost Trends")
            trend_table.add_column("Period", style="cyan")
            trend_table.add_column("Total Cost", style="green")
            trend_table.add_column("Avg Daily", style="yellow")
            trend_table.add_column("Change %", style="magenta")
            trend_table.add_column("Direction", style="blue")
            
            for trend in trends[:10]:  # Show top 10 trends
                direction_color = "red" if trend.trend_direction == "increasing" else "green"
                trend_table.add_row(
                    trend.period,
                    f"${trend.total_cost:.4f}",
                    f"${trend.avg_daily_cost:.4f}",
                    f"{trend.cost_change_percent:+.1f}%",
                    f"[{direction_color}]{trend.trend_direction}[/{direction_color}]"
                )
                
            console.print(trend_table)
        else:
            console.print("   No trend data available")
            
        # Detect cost anomalies
        console.print("\n🚨 Cost Anomaly Detection")
        console.print("=" * 40)
        anomalies = cost_history.detect_cost_anomalies(days=days)
        
        if anomalies:
            anomaly_table = Table(title="🚨 Detected Anomalies")
            anomaly_table.add_column("Date", style="cyan")
            anomaly_table.add_column("Type", style="red")
            anomaly_table.add_column("Severity", style="yellow")
            anomaly_table.add_column("Cost Difference", style="magenta")
            anomaly_table.add_column("Confidence", style="blue")
            
            for anomaly in anomalies[:10]:  # Show top 10 anomalies
                severity_color = {
                    "low": "green",
                    "medium": "yellow",
                    "high": "red",
                    "critical": "red"
                }.get(anomaly.severity, "white")
                
                anomaly_table.add_row(
                    anomaly.timestamp[:10],
                    anomaly.anomaly_type,
                    f"[{severity_color}]{anomaly.severity}[/{severity_color}]",
                    f"${anomaly.cost_difference:.4f}",
                    f"{anomaly.confidence_score:.1%}"
                )
                
            console.print(anomaly_table)
        else:
            console.print("   ✅ No anomalies detected")
            
        # Cost breakdown by granularity
        console.print("\n📅 Cost Breakdown by Time Period")
        console.print("=" * 40)
        
        for granularity in [TimeGranularity.WEEKLY, TimeGranularity.MONTHLY]:
            records = cost_history.get_cost_history(days=days, granularity=granularity)
            if records:
                granularity_name = granularity.value.replace('_', ' ').title()
                console.print(f"\n{granularity_name} Breakdown:")
                
                granularity_table = Table()
                granularity_table.add_column("Period", style="cyan")
                granularity_table.add_column("Total Cost", style="green")
                granularity_table.add_column("Queries", style="yellow")
                granularity_table.add_column("Avg Cost", style="magenta")
                
                for record in records[:5]:  # Show top 5 periods
                    granularity_table.add_row(
                        record.date,
                        f"${record.total_cost_usd:.4f}",
                        str(record.total_queries),
                        f"${record.avg_query_cost:.4f}"
                    )
                    
                console.print(granularity_table)
                
    except Exception as e:
        console.print(f"❌ Error displaying cost analytics: {e}")

@cli.command()
@click.option('--days', default=365, help='Number of days to keep')
def cleanup_cost_history(days):
    """Clean up old cost history records"""
    console.print(f"\n🧹 Cleaning up cost history records older than {days} days...")
    
    try:
        cost_history = get_cost_history()
        cost_history.cleanup_old_records(days)
        console.print(f"✅ Cost history cleanup completed successfully")
        
    except Exception as e:
        console.print(f"❌ Error cleaning up cost history: {e}")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
def query_tracking(days):
    """Display query cost tracking dashboard and analytics"""
    console.print(f"\n🔍 Query Cost Tracking Dashboard (Last {days} days)")
    console.print("=" * 60)
    
    try:
        query_tracker = get_query_cost_tracker()
        
        # Display comprehensive dashboard
        query_tracker.display_query_cost_dashboard(days=days)
        
        # Display performance metrics
        console.print(f"\n📈 Performance Metrics (Last {days} days)")
        console.print("=" * 50)
        performance = query_tracker.get_query_performance_metrics(days=days)
        
        if "error" not in performance:
            perf_text = Text()
            perf_text.append(f"Total Queries: {performance['total_queries']}\n", style="bold blue")
            perf_text.append(f"Avg Execution Time: {performance['avg_execution_time_ms']:.0f}ms\n", style="bold green")
            perf_text.append(f"Avg Cost: ${performance['avg_cost_usd']:.4f}\n", style="bold yellow")
            perf_text.append(f"Outliers: {performance['outliers_count']}", style="bold red")
            
            perf_panel = Panel(perf_text, title="⚡ Performance Overview", border_style="green")
            console.print(perf_panel)
            
            # Performance distribution
            if 'performance_distribution' in performance:
                perf_table = Table(title="📊 Performance Distribution")
                perf_table.add_column("Category", style="cyan")
                perf_table.add_column("Count", style="magenta")
                perf_table.add_column("Percentage", style="green")
                
                total = performance['total_queries']
                for category, count in performance['performance_distribution'].items():
                    percentage = (count / total * 100) if total > 0 else 0
                    perf_table.add_row(category.replace('_', ' ').title(), str(count), f"{percentage:.1f}%")
                    
                console.print(perf_table)
                
            # Cost distribution
            if 'cost_distribution' in performance:
                cost_table = Table(title="💰 Cost Distribution")
                cost_table.add_column("Category", style="cyan")
                cost_table.add_column("Count", style="magenta")
                cost_table.add_column("Percentage", style="green")
                
                for category, count in performance['cost_distribution'].items():
                    percentage = (count / total * 100) if total > 0 else 0
                    cost_table.add_row(category.replace('_', ' ').title(), str(count), f"{percentage:.1f}%")
                    
                console.print(cost_table)
        else:
            console.print(f"❌ Error getting performance metrics: {performance['error']}")
            
    except Exception as e:
        console.print(f"❌ Error displaying query tracking dashboard: {e}")

@cli.command()
@click.option('--days', default=30, help='Number of days to analyze')
def query_analytics(days):
    """Advanced query cost analytics and insights"""
    console.print(f"\n📊 Advanced Query Cost Analytics (Last {days} days)")
    console.print("=" * 60)
    
    try:
        query_tracker = get_query_cost_tracker()
        
        # Get comprehensive summary
        summary = query_tracker.get_query_cost_summary(days=days)
        if "error" in summary:
            console.print(f"❌ Error: {summary['error']}")
            return
            
        # Cost accuracy analysis
        console.print("\n🎯 Cost Accuracy Analysis")
        console.print("=" * 40)
        accuracy_text = Text()
        accuracy_text.append(f"Cost Accuracy: {summary['cost_accuracy_percent']:.1f}%\n", style="bold blue")
        accuracy_text.append(f"Total Estimated: ${summary['total_estimated_usd']:.4f}\n", style="bold green")
        accuracy_text.append(f"Total Actual: ${summary['total_cost_usd']:.4f}\n", style="bold yellow")
        accuracy_text.append(f"Difference: ${summary['cost_difference_usd']:.4f}", style="bold red")
        
        accuracy_panel = Panel(accuracy_text, title="🎯 Accuracy Metrics", border_style="blue")
        console.print(accuracy_panel)
        
        # Cost trends analysis
        if 'cost_trends' in summary and 'error' not in summary['cost_trends']:
            trends = summary['cost_trends']
            console.print("\n📈 Cost Trends Analysis")
            console.print("=" * 40)
            
            trend_text = Text()
            trend_text.append(f"Overall Trend: {trends['trend'].title()}\n", style="bold blue")
            trend_text.append(f"Cost Change: {trends['cost_change_percent']:+.1f}%\n", style="bold green")
            
            if trends['date_range']['start'] and trends['date_range']['end']:
                trend_text.append(f"Analysis Period: {trends['date_range']['start']} to {trends['date_range']['end']}\n", style="bold yellow")
                
            # Daily cost breakdown
            if 'daily_costs' in trends:
                daily_table = Table(title="📅 Daily Cost Breakdown")
                daily_table.add_column("Date", style="cyan")
                daily_table.add_column("Cost", style="green")
                daily_table.add_column("Query Count", style="magenta")
                
                # Sort by date and show last 10 days
                sorted_dates = sorted(trends['daily_costs'].keys(), reverse=True)[:10]
                for date in sorted_dates:
                    data = trends['daily_costs'][date]
                    daily_table.add_row(date, f"${data['cost']:.4f}", str(data['count']))
                    
                console.print(daily_table)
                
        # Most expensive queries
        console.print("\n💸 Most Expensive Queries Analysis")
        console.print("=" * 50)
        expensive_queries = query_tracker.get_expensive_queries(limit=10, days=days)
        
        if expensive_queries:
            expensive_table = Table(title="💸 Top 10 Most Expensive Queries")
            expensive_table.add_column("Rank", style="cyan")
            expensive_table.add_column("Type", style="magenta")
            expensive_table.add_column("Cost", style="red")
            expensive_table.add_column("Execution Time", style="yellow")
            expensive_table.add_column("Priority", style="green")
            
            for i, record in enumerate(expensive_queries, 1):
                priority_color = "red" if record.priority == "critical" else "yellow" if record.priority == "high" else "green"
                expensive_table.add_row(
                    str(i),
                    record.query_type,
                    f"${record.actual_cost_usd:.4f}",
                    f"{record.execution_time_ms}ms",
                    f"[bold {priority_color}]{record.priority}[/bold {priority_color}]"
                )
                
            console.print(expensive_table)
        else:
            console.print("ℹ️  No expensive queries found in the specified period")
            
        # Query type analysis
        if 'cost_by_type' in summary:
            console.print("\n🔍 Query Type Cost Analysis")
            console.print("=" * 40)
            
            type_table = Table(title="📊 Cost Breakdown by Query Type")
            type_table.add_column("Query Type", style="cyan")
            type_table.add_column("Count", style="magenta")
            type_table.add_column("Total Cost", style="green")
            type_table.add_column("Avg Cost", style="yellow")
            type_table.add_column("Cost %", style="blue")
            
            total_cost = summary['total_cost_usd']
            for query_type, data in summary['cost_by_type'].items():
                cost_percentage = (data['total_cost'] / total_cost * 100) if total_cost > 0 else 0
                type_table.add_row(
                    query_type,
                    str(data['count']),
                    f"${data['total_cost']:.4f}",
                    f"${data['avg_cost']:.4f}",
                    f"{cost_percentage:.1f}%"
                )
                
            console.print(type_table)
            
    except Exception as e:
        console.print(f"❌ Error displaying query analytics: {e}")

@cli.command()
def costs():
    """Show detailed cost information and billing status"""
    console.print("\n💰 Cost Monitoring Dashboard")
    console.print("=" * 50)
    
    try:
        cost_monitor = get_cost_monitor()
        cost_monitor.display_cost_dashboard()
        
    except Exception as e:
        console.print(f"❌ Error displaying cost dashboard: {e}")

@cli.command()
def reset_costs():
    """Reset daily cost tracking (useful for testing)"""
    console.print("\n🔄 Resetting daily cost tracking...")
    
    try:
        cost_monitor = get_cost_monitor()
        cost_monitor.reset_daily_costs()
        console.print("✅ Daily costs reset successfully")
        
    except Exception as e:
        console.print(f"❌ Error resetting costs: {e}")

@cli.command()
@click.option('--report-id', default='RPT001', help='Threat report ID to analyze')
def analyze_threat(report_id):
    """Analyze threat using AI processing"""
    console.print(f"\n🔍 Analyzing threat: {report_id}")
    
    try:
        ai_processor = get_ai_processor()
        
        # Generate threat indicators
        console.print("🔍 Generating threat indicators...")
        indicators_result = ai_processor.generate_threat_indicators(report_id)
        
        if indicators_result["success"]:
            console.print("✅ Threat indicators generated")
            console.print(f"💰 Cost: ${indicators_result['cost_usd']:.4f}")
            
            # Display results
            ai_processor.display_threat_indicators(indicators_result["data"])
        else:
            console.print(f"❌ Threat indicators failed: {indicators_result['error']}")
            
        # Generate executive briefing
        console.print("\n📋 Generating executive briefing...")
        briefing_result = ai_processor.generate_executive_briefing("TechCorp Solutions")
        
        if briefing_result["success"]:
            console.print("✅ Executive briefing generated")
            console.print(f"💰 Cost: ${briefing_result['cost_usd']:.4f}")
            
            # Display results
            ai_processor.display_executive_briefing(briefing_result["data"])
        else:
            console.print(f"❌ Executive briefing failed: {briefing_result['error']}")
            
    except Exception as e:
        console.print(f"❌ Error analyzing threat: {e}")

@cli.command()
@click.option('--vendor-id', default='V001', help='Vendor ID to analyze')
def analyze_vendor(vendor_id):
    """Analyze vendor infrastructure using multimodal AI"""
    console.print(f"\n🏗️ Analyzing vendor infrastructure: {vendor_id}")
    
    try:
        multimodal_processor = get_multimodal_processor()
        
        # Analyze infrastructure diagrams
        console.print("🔍 Analyzing infrastructure security...")
        infrastructure_result = multimodal_processor.analyze_infrastructure_diagrams(vendor_id)
        
        if infrastructure_result["success"]:
            console.print("✅ Infrastructure analysis completed")
            console.print(f"💰 Cost: ${infrastructure_result['cost_usd']:.4f}")
            
            # Display results
            multimodal_processor.display_infrastructure_analysis(infrastructure_result["data"])
        else:
            console.print(f"❌ Infrastructure analysis failed: {infrastructure_result['error']}")
            
        # Correlate cyber-physical threats
        console.print("\n🔗 Correlating cyber-physical threats...")
        correlation_result = multimodal_processor.correlate_cyber_physical_threats(vendor_id)
        
        if correlation_result["success"]:
            console.print("✅ Cyber-physical correlation completed")
            console.print(f"💰 Cost: ${correlation_result['cost_usd']:.4f}")
            
            # Display results
            multimodal_processor.display_cyber_physical_correlation(correlation_result["data"])
        else:
            console.print(f"❌ Cyber-physical correlation failed: {correlation_result['error']}")
            
    except Exception as e:
        console.print(f"❌ Error analyzing vendor: {e}")

@cli.command()
@click.option('--report-id', default='RPT001', help='Threat report ID for vector analysis')
def vector_search(report_id):
    """Perform vector similarity search for threats"""
    console.print(f"\n🔍 Performing vector similarity search for: {report_id}")
    
    try:
        vector_processor = get_vector_processor()
        
        # Find similar threats
        console.print("🔍 Finding similar threats...")
        similarity_result = vector_processor.find_similar_threats(report_id)
        
        if similarity_result["success"]:
            console.print("✅ Similar threats found")
            console.print(f"💰 Cost: ${similarity_result['cost_usd']:.4f}")
            
            # Display results
            vector_processor.display_similarity_results(similarity_result["data"], report_id)
        else:
            console.print(f"❌ Vector search failed: {similarity_result['error']}")
            
        # Analyze threat patterns
        console.print("\n📊 Analyzing threat patterns...")
        patterns_result = vector_processor.analyze_threat_patterns()
        
        if patterns_result["success"]:
            console.print("✅ Threat pattern analysis completed")
            console.print(f"💰 Cost: ${patterns_result['cost_usd']:.4f}")
        else:
            console.print(f"❌ Pattern analysis failed: {patterns_result['error']}")
            
    except Exception as e:
        console.print(f"❌ Error performing vector search: {e}")

@cli.command()
def export_data():
    """Export all AI-enhanced data to JSON files"""
    console.print("\n📁 Exporting AI-enhanced data...")
    
    try:
        data_exporter = get_data_exporter()
        
        # Export threat data
        console.print("📊 Exporting threat data...")
        threat_result = data_exporter.export_threat_data()
        
        if threat_result["success"]:
            console.print("✅ Threat data exported")
            console.print(f"💰 Cost: ${threat_result['cost_usd']:.4f}")
        else:
            console.print(f"❌ Threat export failed: {threat_result['error']}")
            
        # Export vendor data
        console.print("\n🏗️ Exporting vendor data...")
        vendor_result = data_exporter.export_vendor_data()
        
        if vendor_result["success"]:
            console.print("✅ Vendor data exported")
            console.print(f"💰 Cost: ${vendor_result['cost_usd']:.4f}")
        else:
            console.print(f"❌ Vendor export failed: {vendor_result['error']}")
            
        # Export analytics data
        console.print("\n📈 Exporting analytics data...")
        analytics_result = data_exporter.export_analytics_data()
        
        if analytics_result["success"]:
            console.print("✅ Analytics data exported")
            console.print(f"💰 Cost: ${analytics_result['cost_usd']:.4f}")
        else:
            console.print(f"❌ Analytics export failed: {analytics_result['error']}")
            
    except Exception as e:
        console.print(f"❌ Error exporting data: {e}")

@cli.command()
def demo():
    """Run complete AI processing demo pipeline"""
    console.print("\n🎬 Running Complete AI Processing Demo Pipeline")
    console.print("=" * 60)
    
    try:
        # Setup environment
        console.print("🔧 Setting up environment...")
        setup()
        
        # Analyze threats
        console.print("\n🔍 Analyzing threats...")
        analyze_threat("RPT001")
        
        # Analyze vendors
        console.print("\n🏗️ Analyzing vendors...")
        analyze_vendor("V001")
        
        # Vector search
        console.print("\n🔍 Performing vector search...")
        vector_search("RPT001")
        
        # Export data
        console.print("\n📁 Exporting data...")
        export_data()
        
        # Show final status
        console.print("\n📊 Final system status...")
        status()
        
        console.print("\n🎉 Demo pipeline completed successfully!")
        
    except Exception as e:
        console.print(f"❌ Demo pipeline failed: {e}")

if __name__ == "__main__":
    cli()
