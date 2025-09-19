"""
Cost monitoring module for BigQuery AI processing
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from config import config, cost_config
from billing_service import get_billing_service
from query_cost_tracker import get_query_cost_tracker
from budget_enforcer import get_budget_enforcer
from cost_history import get_cost_history

console = Console()

class CostMonitor:
    """Monitor and control BigQuery AI processing costs"""
    
    def __init__(self):
        self.client = bigquery.Client(project=config.gcp_project_id)
        self.billing_service = get_billing_service()
        self.query_tracker = get_query_cost_tracker()
        self.budget_enforcer = get_budget_enforcer()
        self.cost_history = get_cost_history()
        self.cost_log_file = "cost_log.json"
        self.daily_costs: Dict[str, float] = {}
        self.query_costs: List[Dict] = []
        self.load_cost_history()
        
    def load_cost_history(self):
        """Load cost history from file"""
        try:
            if os.path.exists(self.cost_log_file):
                with open(self.cost_log_file, 'r') as f:
                    data = json.load(f)
                    self.daily_costs = data.get('daily_costs', {})
                    self.query_costs = data.get('query_costs', [])
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load cost history: {e}")
            
    def save_cost_history(self):
        """Save cost history to file"""
        try:
            data = {
                'daily_costs': self.daily_costs,
                'query_costs': self.query_costs,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cost_log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save cost history: {e}")
            
    def get_daily_cost(self, date: str = None) -> float:
        """Get cost for a specific date - now integrates with real-time billing"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # Try to get real-time cost first
        try:
            real_time_costs = self.billing_service.get_daily_cost_breakdown(date)
            if "error" not in real_time_costs:
                return real_time_costs["total_cost"]
        except Exception as e:
            console.print(f"⚠️  Could not get real-time costs: {e}")
            
        # Fallback to cached costs
        return self.daily_costs.get(date, 0.0)
        
    def add_query_cost(self, query: str, cost_usd: float, query_type: str = "unknown", 
                       job=None, execution_time_ms: int = 0, error_message: Optional[str] = None):
        """Add cost for a specific query with enhanced tracking and budget enforcement"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update daily cost
        self.daily_costs[today] = self.daily_costs.get(today, 0.0) + cost_usd
        
        # Log query cost (legacy format)
        query_record = {
            'timestamp': datetime.now().isoformat(),
            'query_type': query_type,
            'cost_usd': cost_usd,
            'daily_total': self.daily_costs[today],
            'query_preview': query[:100] + "..." if len(query) > 100 else query
        }
        self.query_costs.append(query_record)
        
        # Enhanced query cost tracking
        try:
            self.query_tracker.track_query_execution(
                query=query,
                query_type=query_type,
                job=job,
                execution_time_ms=execution_time_ms,
                error_message=error_message
            )
        except Exception as e:
            console.print(f"⚠️  Warning: Could not track query execution: {e}")
        
        # Enforce budget rules after cost addition
        try:
            violations = self.budget_enforcer.enforce_budget_rules(cost_usd, query_type)
            if violations:
                console.print(f"🚨 {len(violations)} budget violations detected after query execution")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not enforce budget rules: {e}")
        
        # Save after each update
        self.save_cost_history()
        
        # Check legacy budget alerts (for backward compatibility)
        self.check_budget_alerts(today)
        
        # Record cost in history system
        try:
            self.cost_history.record_daily_cost(today)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not record cost in history: {e}")
        
    def check_budget_alerts(self, date: str):
        """Check if budget limits are exceeded and send alerts (legacy method)"""
        daily_cost = self.daily_costs.get(date, 0.0)
        budget_limit = config.daily_budget_limit_usd
        
        if daily_cost >= budget_limit:
            console.print(f"🚨 CRITICAL: Daily budget limit exceeded! ${daily_cost:.4f} / ${budget_limit}")
            return False
        elif daily_cost >= budget_limit * (cost_config.critical_threshold_percent / 100):
            console.print(f"⚠️  WARNING: Approaching daily budget limit! ${daily_cost:.4f} / ${budget_limit}")
        elif daily_cost >= budget_limit * (cost_config.warning_threshold_percent / 100):
            console.print(f"⚠️  NOTICE: Daily budget usage: ${daily_cost:.4f} / ${budget_limit}")
            
        return True
        
    def can_execute_query(self, estimated_cost_usd: float) -> Tuple[bool, str]:
        """Check if a query can be executed within budget constraints using budget enforcer"""
        try:
            # Use the budget enforcer for comprehensive budget checking
            can_execute, message, enforcement_action = self.budget_enforcer.can_execute_query(estimated_cost_usd)
            
            # Log the budget check
            if not can_execute:
                console.print(f"🚫 Budget enforcement: {message}")
            elif enforcement_action == EnforcementAction.WARN:
                console.print(f"⚠️  Budget warning: {message}")
                
            return can_execute, message
            
        except Exception as e:
            console.print(f"❌ Error checking budget constraints: {e}")
            # Fallback to legacy method
            return self._legacy_budget_check(estimated_cost_usd)
            
    def _legacy_budget_check(self, estimated_cost_usd: float) -> Tuple[bool, str]:
        """Legacy budget checking method (fallback)"""
        today = datetime.now().strftime('%Y-%m-%d')
        current_daily_cost = self.daily_costs.get(today, 0.0)
        
        # Check daily budget limit
        if current_daily_cost + estimated_cost_usd > config.daily_budget_limit_usd:
            return False, f"Daily budget limit would be exceeded: ${current_daily_cost:.4f} + ${estimated_cost_usd:.4f} > ${config.daily_budget_limit_usd}"
            
        # Check per-query cost limit
        if estimated_cost_usd > config.max_query_cost_usd:
            return False, f"Query cost exceeds limit: ${estimated_cost_usd:.4f} > ${config.max_query_cost_usd}"
            
        return True, "Query can be executed"
        
    def estimate_query_cost(self, query: str) -> float:
        """Estimate the cost of a BigQuery query using dry-run"""
        try:
            job_config = QueryJobConfig(dry_run=True)
            job = self.client.query(query, job_config=job_config)
            
            # Calculate cost based on bytes processed
            bytes_processed = job.total_bytes_processed
            cost_usd = (bytes_processed / (1024**3)) * 5.0  # $5 per TB
            
            return cost_usd
            
        except Exception as e:
            console.print(f"⚠️  Warning: Could not estimate query cost: {e}")
            return 0.0
            
    def get_cost_summary(self) -> Dict:
        """Get comprehensive cost summary - now includes real-time billing data, query tracking, and budget enforcement"""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Try to get real-time costs
        real_time_costs = None
        try:
            real_time_costs = self.billing_service.get_real_time_costs(days=7)
        except Exception as e:
            console.print(f"⚠️  Could not get real-time costs: {e}")
            
        # Get today's cost (real-time if available, fallback to cached)
        today_cost = self.get_daily_cost(today)
        
        # Calculate budget usage
        budget_limit = config.daily_budget_limit_usd
        remaining_budget = max(0, budget_limit - today_cost)
        usage_percent = min(100, (today_cost / budget_limit) * 100) if budget_limit > 0 else 0
        
        summary = {
            'today': {
                'date': today,
                'cost_usd': today_cost,
                'budget_limit_usd': budget_limit,
                'remaining_usd': remaining_budget,
                'usage_percent': usage_percent
            },
            'yesterday': {
                'date': yesterday,
                'cost_usd': self.daily_costs.get(yesterday, 0.0)
            },
            'total_queries': len(self.query_costs),
            'average_query_cost': sum(q['cost_usd'] for q in self.query_costs) / len(self.query_costs) if self.query_costs else 0.0
        }
        
        # Add real-time billing data if available
        if real_time_costs and "error" not in real_time_costs:
            summary['real_time_billing'] = {
                'billing_account': real_time_costs.get('billing_account'),
                'bigquery_costs': real_time_costs.get('bigquery_costs', {}),
                'project_costs': real_time_costs.get('project_costs', {}),
                'total_real_time_cost': real_time_costs.get('total_costs', {}).get('overall', 0.0),
                'cache_info': real_time_costs.get('cache_info', {})
            }
            
        # Add query tracking data
        try:
            query_summary = self.query_tracker.get_query_cost_summary(days=30)
            if "error" not in query_summary:
                summary['query_tracking'] = {
                    'total_tracked_queries': query_summary.get('total_queries', 0),
                    'tracked_cost_usd': query_summary.get('total_cost_usd', 0.0),
                    'cost_accuracy_percent': query_summary.get('cost_accuracy_percent', 0.0),
                    'avg_execution_time_ms': query_summary.get('avg_execution_time_ms', 0.0)
                }
        except Exception as e:
            console.print(f"⚠️  Could not get query tracking summary: {e}")
            
        # Add budget enforcement data
        try:
            budget_status = self.budget_enforcer.get_current_budget_status()
            if "error" not in budget_status:
                summary['budget_enforcement'] = {
                    'overall_status': budget_status.get('overall_status', 'unknown'),
                    'active_rules': len([r for r in self.budget_enforcer.budget_rules if r.enabled]),
                    'total_rules': len(self.budget_enforcer.budget_rules),
                    'current_costs': budget_status.get('current_costs', {}),
                    'rule_statuses': budget_status.get('rule_statuses', [])
                }
                
            # Get enforcement summary
            enforcement_summary = self.budget_enforcer.get_enforcement_summary(days=30)
            if "error" not in enforcement_summary:
                summary['enforcement_summary'] = enforcement_summary
                
        except Exception as e:
            console.print(f"⚠️  Could not get budget enforcement data: {e}")
            
        # Add cost history data
        try:
            cost_history_status = self.get_cost_history_status()
            if cost_history_status.get('cost_history_enabled', False):
                summary['cost_history'] = {
                    'total_history_records': cost_history_status.get('total_history_records', 0),
                    'history_period_days': cost_history_status.get('history_period_days', 0),
                    'trends_analyzed': cost_history_status.get('trends_analyzed', 0),
                    'anomalies_detected': cost_history_status.get('anomalies_detected', 0)
                }
        except Exception as e:
            console.print(f"⚠️  Could not get cost history data: {e}")
            
        return summary
        
    def display_cost_dashboard(self):
        """Display enhanced cost monitoring dashboard with real-time billing, query tracking, and budget enforcement"""
        try:
            # Display real-time billing dashboard
            console.print("\n🏦 Real-Time Billing Dashboard")
            console.print("=" * 50)
            self.billing_service.display_billing_dashboard()
            
            # Display local cost tracking
            console.print("\n📊 Local Cost Tracking")
            console.print("=" * 50)
            summary = self.get_cost_summary()
            
            # Create cost overview panel
            cost_text = Text()
            cost_text.append(f"Today's Cost: ${summary['today']['cost_usd']:.4f}\n", style="bold blue")
            cost_text.append(f"Budget Limit: ${summary['today']['budget_limit_usd']:.2f}\n", style="bold green")
            cost_text.append(f"Remaining: ${summary['today']['remaining_usd']:.4f}\n", style="bold yellow")
            cost_text.append(f"Usage: {summary['today']['usage_percent']:.1f}%", style="bold red" if summary['today']['usage_percent'] > 80 else "bold green")
            
            cost_panel = Panel(cost_text, title="💰 Cost Overview", border_style="blue")
            console.print(cost_panel)
            
            # Display budget enforcement dashboard
            console.print("\n🚨 Budget Enforcement")
            console.print("=" * 50)
            self.budget_enforcer.display_budget_dashboard()
            
            # Display query tracking dashboard
            console.print("\n🔍 Query Cost Tracking")
            console.print("=" * 50)
            self.query_tracker.display_query_cost_dashboard(days=30)
            
            # Display cost history dashboard
            console.print("\n📊 Cost History Dashboard")
            console.print("=" * 50)
            self.display_cost_history_dashboard(days=30)
            
            # Create recent queries table
            if self.query_costs:
                table = Table(title="📊 Recent Query Costs")
                table.add_column("Time", style="cyan")
                table.add_column("Type", style="magenta")
                table.add_column("Cost", style="green")
                table.add_column("Daily Total", style="yellow")
                
                # Show last 10 queries
                for query in self.query_costs[-10:]:
                    time_str = datetime.fromisoformat(query['timestamp']).strftime('%H:%M:%S')
                    table.add_row(
                        time_str,
                        query['query_type'],
                        f"${query['cost_usd']:.4f}",
                        f"${query['daily_total']:.4f}"
                    )
                    
                console.print(table)
                
            # Display cost alerts
            alerts = self.billing_service.get_cost_alerts()
            if alerts and "error" not in alerts[0]:
                console.print("\n🚨 Cost Alerts")
                console.print("=" * 50)
                for alert in alerts:
                    level_color = "red" if alert["level"] == "critical" else "yellow" if alert["level"] == "warning" else "blue"
                    console.print(f"[bold {level_color}]{alert['level'].upper()}:[/bold {level_color}] {alert['message']}")
                    
        except Exception as e:
            console.print(f"❌ Error displaying cost dashboard: {e}")
            
    def reset_daily_costs(self):
        """Reset daily costs (useful for testing)"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_costs[today] = 0.0
        self.save_cost_history()
        console.print(f"✅ Reset daily costs for {today}")
        
    def get_budget_status(self) -> str:
        """Get current budget status for API responses"""
        try:
            # Use budget enforcer for comprehensive status
            budget_status = self.budget_enforcer.get_current_budget_status()
            if "error" not in budget_status:
                return budget_status.get('overall_status', 'unknown')
        except Exception as e:
            console.print(f"⚠️  Could not get budget enforcement status: {e}")
            
        # Fallback to legacy method
        summary = self.get_cost_summary()
        usage_percent = summary['today']['usage_percent']
        
        if usage_percent >= 100:
            return "exceeded"
        elif usage_percent >= 95:
            return "critical"
        elif usage_percent >= 80:
            return "warning"
        else:
            return "healthy"
            
    def cleanup_old_records(self, days_to_keep: int = 30):
        """Clean up old cost records to prevent file bloat"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean daily costs
        old_dates = [date for date in self.daily_costs.keys() 
                    if datetime.fromisoformat(date + "T00:00:00") < cutoff_date]
        for date in old_dates:
            del self.daily_costs[date]
            
        # Clean query costs
        self.query_costs = [q for q in self.query_costs 
                           if datetime.fromisoformat(q['timestamp']) > cutoff_date]
                           
        self.save_cost_history()
        console.print(f"🧹 Cleaned up cost records older than {days_to_keep} days")
        
        # Clean up query tracking records
        try:
            self.query_tracker.cleanup_old_records(days_to_keep=90)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not cleanup query tracking records: {e}")
            
        # Clean up budget violations
        try:
            self.budget_enforcer.cleanup_old_violations(days_to_keep=90)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not cleanup budget violations: {e}")
            
        # Clean up cost history records
        try:
            self.cleanup_cost_history(days_to_keep=365)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not cleanup cost history: {e}")
        
    def get_billing_status(self) -> Dict:
        """Get billing service status and configuration"""
        try:
            billing_account = self.billing_service.get_billing_account()
            billing_export_status = self.billing_service.setup_billing_export()
            
            return {
                "billing_account": billing_account,
                "billing_export": billing_export_status,
                "real_time_available": billing_account is not None,
                "cost_tracking_method": "real_time" if billing_account else "estimated"
            }
        except Exception as e:
            return {
                "error": str(e),
                "real_time_available": False,
                "cost_tracking_method": "estimated"
            }
            
    def get_query_tracking_status(self) -> Dict:
        """Get query cost tracking status and metrics"""
        try:
            summary = self.query_tracker.get_query_cost_summary(days=30)
            performance = self.query_tracker.get_query_performance_metrics(days=30)
            
            return {
                "query_tracking_enabled": True,
                "total_tracked_queries": summary.get('total_queries', 0) if "error" not in summary else 0,
                "tracked_cost_usd": summary.get('total_cost_usd', 0.0) if "error" not in summary else 0.0,
                "cost_accuracy_percent": summary.get('cost_accuracy_percent', 0.0) if "error" not in summary else 0.0,
                "performance_metrics": performance if "error" not in performance else {},
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "query_tracking_enabled": False
            }
            
    def get_budget_enforcement_status(self) -> Dict:
        """Get budget enforcement status and metrics"""
        try:
            budget_status = self.budget_enforcer.get_current_budget_status()
            enforcement_summary = self.budget_enforcer.get_enforcement_summary(days=30)
            
            return {
                "budget_enforcement_enabled": True,
                "overall_status": budget_status.get('overall_status', 'unknown') if "error" not in budget_status else 'unknown',
                "active_rules": len([r for r in self.budget_enforcer.budget_rules if r.enabled]),
                "total_rules": len(self.budget_enforcer.budget_rules),
                "enforcement_summary": enforcement_summary if "error" not in enforcement_summary else {},
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "budget_enforcement_enabled": False
            }
            
    def get_cost_history_status(self) -> Dict:
        """Get cost history status and metrics"""
        try:
            summary = self.cost_history.get_cost_summary(days=30)
            trends = self.cost_history.analyze_cost_trends(days=30)
            anomalies = self.cost_history.detect_cost_anomalies(days=30)
            
            return {
                "cost_history_enabled": True,
                "total_history_records": len(self.cost_history.cost_records),
                "history_period_days": 30,
                "cost_summary": summary if "error" not in summary else {},
                "trends_analyzed": len(trends),
                "anomalies_detected": len(anomalies),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "cost_history_enabled": False
            }
            
    def display_cost_history_dashboard(self, days: int = 30):
        """Display cost history dashboard"""
        try:
            self.cost_history.display_cost_history_dashboard(days)
        except Exception as e:
            console.print(f"❌ Error displaying cost history dashboard: {e}")
            
    def cleanup_cost_history(self, days_to_keep: int = 365):
        """Clean up old cost history records"""
        try:
            self.cost_history.cleanup_old_records(days_to_keep)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not cleanup cost history: {e}")

# Global cost monitor instance
cost_monitor = CostMonitor()

def get_cost_monitor() -> CostMonitor:
    """Get global cost monitor instance"""
    return cost_monitor
