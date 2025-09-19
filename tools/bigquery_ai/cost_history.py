#!/usr/bin/env python3
"""
Cost History System for BigQuery AI processing
Provides comprehensive historical spending data and analytics
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import config, cost_config
from billing_service import get_billing_service
from query_cost_tracker import get_query_cost_tracker
from budget_enforcer import get_budget_enforcer

console = Console()

class TimeGranularity(Enum):
    """Time granularity for cost history"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class CostCategory(Enum):
    """Cost categories for classification"""
    DATA_PROCESSING = "data_processing"
    COMPUTE_SLOTS = "compute_slots"
    STORAGE = "storage"
    NETWORK = "network"
    AI_MODELS = "ai_models"
    OTHER = "other"

@dataclass
class CostHistoryRecord:
    """Historical cost record with detailed breakdown"""
    record_id: str
    timestamp: str
    date: str  # YYYY-MM-DD format for easy grouping
    
    # Cost breakdown
    total_cost_usd: float
    data_processing_cost: float
    compute_slots_cost: float
    storage_cost: float
    network_cost: float
    ai_models_cost: float
    other_costs: float
    
    # Usage metrics
    bytes_processed: int
    slot_ms: int
    storage_bytes: int
    network_bytes: int
    
    # Query metrics
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_query_cost: float
    max_query_cost: float
    
    # Budget metrics
    budget_limit: float
    budget_used: float
    budget_remaining: float
    budget_utilization_percent: float
    
    # Tags and metadata
    tags: List[str]
    cost_center: Optional[str]
    project_id: str
    environment: str  # dev, staging, prod
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostHistoryRecord':
        return cls(**data)

@dataclass
class CostTrend:
    """Cost trend analysis result"""
    period: str
    start_date: str
    end_date: str
    total_cost: float
    avg_daily_cost: float
    cost_change_percent: float
    trend_direction: str  # increasing, decreasing, stable
    peak_cost: float
    peak_date: str
    low_cost: float
    low_date: str
    cost_variance: float
    forecast_next_period: float

@dataclass
class CostAnomaly:
    """Cost anomaly detection result"""
    anomaly_id: str
    timestamp: str
    anomaly_type: str  # spike, drop, unusual_pattern
    severity: str  # low, medium, high, critical
    description: str
    cost_difference: float
    percentage_change: float
    expected_cost: float
    actual_cost: float
    confidence_score: float
    recommended_action: str

class CostHistory:
    """Comprehensive cost history tracking and analytics system"""
    
    def __init__(self):
        self.billing_service = get_billing_service()
        self.query_tracker = get_query_cost_tracker()
        self.budget_enforcer = get_budget_enforcer()
        
        self.history_file = "cost_history.json"
        self.analytics_file = "cost_analytics.json"
        self.cost_records: List[CostHistoryRecord] = []
        self.cost_trends: List[CostTrend] = []
        self.cost_anomalies: List[CostAnomaly] = []
        
        self.load_cost_history()
        self.load_cost_analytics()
        
    def load_cost_history(self):
        """Load cost history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.cost_records = [CostHistoryRecord.from_dict(record) for record in data]
                    console.print(f"✅ Loaded {len(self.cost_records)} cost history records")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load cost history: {e}")
            
    def save_cost_history(self):
        """Save cost history to file"""
        try:
            data = [record.to_dict() for record in self.cost_records]
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save cost history: {e}")
            
    def load_cost_analytics(self):
        """Load cost analytics from file"""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r') as f:
                    data = json.load(f)
                    self.cost_trends = [CostTrend(**trend) for trend in data.get('trends', [])]
                    self.cost_anomalies = [CostAnomaly(**anomaly) for anomaly in data.get('anomalies', [])]
                    console.print(f"✅ Loaded {len(self.cost_trends)} cost trends and {len(self.cost_anomalies)} anomalies")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load cost analytics: {e}")
            
    def save_cost_analytics(self):
        """Save cost analytics to file"""
        try:
            data = {
                'trends': [trend.__dict__ for trend in self.cost_trends],
                'anomalies': [anomaly.__dict__ for anomaly in self.cost_anomalies]
            }
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save cost analytics: {e}")
            
    def record_daily_cost(self, date: Optional[str] = None) -> CostHistoryRecord:
        """Record daily cost summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # Get current cost data
        cost_summary = self.query_tracker.get_query_cost_summary(days=1)
        budget_status = self.budget_enforcer.get_current_budget_status()
        
        # Calculate daily totals
        daily_costs = self.query_tracker.get_daily_cost_breakdown(date)
        
        # Create cost record
        record = CostHistoryRecord(
            record_id=f"cost_{date}_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            date=date,
            
            # Cost breakdown
            total_cost_usd=daily_costs.get('total_cost', 0.0),
            data_processing_cost=daily_costs.get('data_processing_cost', 0.0),
            compute_slots_cost=daily_costs.get('compute_slots_cost', 0.0),
            storage_cost=daily_costs.get('storage_cost', 0.0),
            network_cost=daily_costs.get('network_cost', 0.0),
            ai_models_cost=daily_costs.get('ai_models_cost', 0.0),
            other_costs=daily_costs.get('other_costs', 0.0),
            
            # Usage metrics
            bytes_processed=daily_costs.get('bytes_processed', 0),
            slot_ms=daily_costs.get('slot_ms', 0),
            storage_bytes=daily_costs.get('storage_bytes', 0),
            network_bytes=daily_costs.get('network_bytes', 0),
            
            # Query metrics
            total_queries=daily_costs.get('total_queries', 0),
            successful_queries=daily_costs.get('successful_queries', 0),
            failed_queries=daily_costs.get('failed_queries', 0),
            avg_query_cost=daily_costs.get('avg_query_cost', 0.0),
            max_query_cost=daily_costs.get('max_query_cost', 0.0),
            
            # Budget metrics
            budget_limit=budget_status.get('daily_budget_limit', 0.0),
            budget_used=daily_costs.get('total_cost', 0.0),
            budget_remaining=budget_status.get('daily_budget_remaining', 0.0),
            budget_utilization_percent=budget_status.get('daily_budget_utilization_percent', 0.0),
            
            # Tags and metadata
            tags=daily_costs.get('tags', []),
            cost_center=daily_costs.get('cost_center'),
            project_id=config.gcp_project_id,
            environment=os.getenv('ENVIRONMENT', 'dev')
        )
        
        # Add to history
        self.cost_records.append(record)
        self.save_cost_history()
        
        return record
        
    def get_cost_history(self, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        granularity: TimeGranularity = TimeGranularity.DAILY) -> List[CostHistoryRecord]:
        """Get cost history for specified period and granularity"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Filter records by date range
        filtered_records = [
            record for record in self.cost_records
            if start_date <= record.date <= end_date
        ]
        
        # Group by granularity if needed
        if granularity != TimeGranularity.DAILY:
            filtered_records = self._group_by_granularity(filtered_records, granularity)
            
        return filtered_records
        
    def _group_by_granularity(self, records: List[CostHistoryRecord], 
                             granularity: TimeGranularity) -> List[CostHistoryRecord]:
        """Group cost records by time granularity"""
        if granularity == TimeGranularity.DAILY:
            return records
            
        grouped_records = []
        grouped_data = {}
        
        for record in records:
            if granularity == TimeGranularity.WEEKLY:
                # Get week start date
                date_obj = datetime.strptime(record.date, '%Y-%m-%d')
                week_start = date_obj - timedelta(days=date_obj.weekday())
                key = week_start.strftime('%Y-%m-%d')
            elif granularity == TimeGranularity.MONTHLY:
                key = record.date[:7]  # YYYY-MM
            elif granularity == TimeGranularity.QUARTERLY:
                date_obj = datetime.strptime(record.date, '%Y-%m-%d')
                quarter = (date_obj.month - 1) // 3 + 1
                key = f"{date_obj.year}-Q{quarter}"
            elif granularity == TimeGranularity.YEARLY:
                key = record.date[:4]  # YYYY
            else:
                key = record.date
                
            if key not in grouped_data:
                grouped_data[key] = {
                    'costs': [],
                    'metrics': {
                        'total_queries': 0,
                        'bytes_processed': 0,
                        'slot_ms': 0
                    }
                }
                
            grouped_data[key]['costs'].append(record)
            grouped_data[key]['metrics']['total_queries'] += record.total_queries
            grouped_data[key]['metrics']['bytes_processed'] += record.bytes_processed
            grouped_data[key]['metrics']['slot_ms'] += record.slot_ms
            
        # Create aggregated records
        for key, data in grouped_data.items():
            total_cost = sum(r.total_cost_usd for r in data['costs'])
            avg_record = CostHistoryRecord(
                record_id=f"grouped_{key}_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                date=key,
                total_cost_usd=total_cost,
                data_processing_cost=sum(r.data_processing_cost for r in data['costs']),
                compute_slots_cost=sum(r.compute_slots_cost for r in data['costs']),
                storage_cost=sum(r.storage_cost for r in data['costs']),
                network_cost=sum(r.network_cost for r in data['costs']),
                ai_models_cost=sum(r.ai_models_cost for r in data['costs']),
                other_costs=sum(r.other_costs for r in data['costs']),
                bytes_processed=data['metrics']['bytes_processed'],
                slot_ms=data['metrics']['slot_ms'],
                storage_bytes=0,
                network_bytes=0,
                total_queries=data['metrics']['total_queries'],
                successful_queries=sum(r.successful_queries for r in data['costs']),
                failed_queries=sum(r.failed_queries for r in data['costs']),
                avg_query_cost=total_cost / data['metrics']['total_queries'] if data['metrics']['total_queries'] > 0 else 0.0,
                max_query_cost=max(r.max_query_cost for r in data['costs']),
                budget_limit=0.0,
                budget_used=total_cost,
                budget_remaining=0.0,
                budget_utilization_percent=0.0,
                tags=[],
                cost_center=None,
                project_id=config.gcp_project_id,
                environment='dev'
            )
            grouped_records.append(avg_record)
            
        return grouped_records
        
    def analyze_cost_trends(self, days: int = 30) -> List[CostTrend]:
        """Analyze cost trends over specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily records for the period
        daily_records = self.get_cost_history(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            TimeGranularity.DAILY
        )
        
        trends = []
        
        # Analyze weekly trends
        weekly_records = self.get_cost_history(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            TimeGranularity.WEEKLY
        )
        
        for i, record in enumerate(weekly_records):
            if i > 0:
                prev_record = weekly_records[i-1]
                cost_change = record.total_cost_usd - prev_record.total_cost_usd
                cost_change_percent = (cost_change / prev_record.total_cost_usd * 100) if prev_record.total_cost_usd > 0 else 0
                
                trend = CostTrend(
                    period=f"Week {i}",
                    start_date=record.date,
                    end_date=record.date,
                    total_cost=record.total_cost_usd,
                    avg_daily_cost=record.total_cost_usd / 7,
                    cost_change_percent=cost_change_percent,
                    trend_direction="increasing" if cost_change > 0 else "decreasing" if cost_change < 0 else "stable",
                    peak_cost=record.total_cost_usd,
                    peak_date=record.date,
                    low_cost=record.total_cost_usd,
                    low_date=record.date,
                    cost_variance=abs(cost_change),
                    forecast_next_period=record.total_cost_usd * (1 + cost_change_percent/100)
                )
                trends.append(trend)
                
        # Analyze monthly trends
        monthly_records = self.get_cost_history(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            TimeGranularity.MONTHLY
        )
        
        for i, record in enumerate(monthly_records):
            if i > 0:
                prev_record = monthly_records[i-1]
                cost_change = record.total_cost_usd - prev_record.total_cost_usd
                cost_change_percent = (cost_change / prev_record.total_cost_usd * 100) if prev_record.total_cost_usd > 0 else 0
                
                trend = CostTrend(
                    period=f"Month {i}",
                    start_date=record.date,
                    end_date=record.date,
                    total_cost=record.total_cost_usd,
                    avg_daily_cost=record.total_cost_usd / 30,
                    cost_change_percent=cost_change_percent,
                    trend_direction="increasing" if cost_change > 0 else "decreasing" if cost_change < 0 else "stable",
                    peak_cost=record.total_cost_usd,
                    peak_date=record.date,
                    low_cost=record.total_cost_usd,
                    low_date=record.date,
                    cost_variance=abs(cost_change),
                    forecast_next_period=record.total_cost_usd * (1 + cost_change_percent/100)
                )
                trends.append(trend)
                
        self.cost_trends = trends
        self.save_cost_analytics()
        
        return trends
        
    def detect_cost_anomalies(self, days: int = 30) -> List[CostAnomaly]:
        """Detect cost anomalies using statistical analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily records for the period
        daily_records = self.get_cost_history(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            TimeGranularity.DAILY
        )
        
        if len(daily_records) < 3:
            return []
            
        # Calculate statistics
        costs = [record.total_cost_usd for record in daily_records]
        mean_cost = sum(costs) / len(costs)
        variance = sum((cost - mean_cost) ** 2 for cost in costs) / len(costs)
        std_dev = variance ** 0.5
        
        anomalies = []
        
        for record in daily_records:
            cost_diff = abs(record.total_cost_usd - mean_cost)
            z_score = cost_diff / std_dev if std_dev > 0 else 0
            
            if z_score > 2.0:  # 2 standard deviations threshold
                anomaly_type = "spike" if record.total_cost_usd > mean_cost else "drop"
                severity = "critical" if z_score > 3.0 else "high" if z_score > 2.5 else "medium"
                
                anomaly = CostAnomaly(
                    anomaly_id=f"anomaly_{record.date}_{int(time.time())}",
                    timestamp=record.timestamp,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description=f"Cost {anomaly_type} detected on {record.date}",
                    cost_difference=cost_diff,
                    percentage_change=(cost_diff / mean_cost * 100) if mean_cost > 0 else 0,
                    expected_cost=mean_cost,
                    actual_cost=record.total_cost_usd,
                    confidence_score=min(z_score / 3.0, 1.0),
                    recommended_action=f"Investigate {anomaly_type} in costs on {record.date}"
                )
                anomalies.append(anomaly)
                
        self.cost_anomalies = anomalies
        self.save_cost_analytics()
        
        return anomalies
        
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive cost summary for specified period"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get records for the period
        records = self.get_cost_history(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            TimeGranularity.DAILY
        )
        
        if not records:
            return {"error": "No cost data available for the specified period"}
            
        # Calculate totals
        total_cost = sum(record.total_cost_usd for record in records)
        total_queries = sum(record.total_queries for record in records)
        total_bytes = sum(record.bytes_processed for record in records)
        
        # Calculate averages
        avg_daily_cost = total_cost / len(records)
        avg_query_cost = total_cost / total_queries if total_queries > 0 else 0
        
        # Get cost breakdown
        cost_breakdown = {
            'data_processing': sum(record.data_processing_cost for record in records),
            'compute_slots': sum(record.compute_slots_cost for record in records),
            'storage': sum(record.storage_cost for record in records),
            'network': sum(record.network_cost for record in records),
            'ai_models': sum(record.ai_models_cost for record in records),
            'other': sum(record.other_costs for record in records)
        }
        
        # Get top expensive days
        expensive_days = sorted(records, key=lambda x: x.total_cost_usd, reverse=True)[:5]
        
        return {
            'period_days': days,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_cost_usd': total_cost,
            'avg_daily_cost_usd': avg_daily_cost,
            'total_queries': total_queries,
            'avg_query_cost_usd': avg_query_cost,
            'total_bytes_processed': total_bytes,
            'cost_breakdown': cost_breakdown,
            'expensive_days': [
                {
                    'date': record.date,
                    'cost': record.total_cost_usd,
                    'queries': record.total_queries
                }
                for record in expensive_days
            ],
            'budget_utilization': {
                'total_budget': sum(record.budget_limit for record in records),
                'total_used': sum(record.budget_used for record in records),
                'avg_utilization': sum(record.budget_utilization_percent for record in records) / len(records)
            }
        }
        
    def display_cost_history_dashboard(self, days: int = 30):
        """Display comprehensive cost history dashboard"""
        console.print("\n📊 Cost History Dashboard")
        console.print("=" * 80)
        
        # Get cost summary
        summary = self.get_cost_summary(days)
        if "error" in summary:
            console.print(f"❌ Error: {summary['error']}")
            return
            
        # Overview panel
        overview_panel = Panel(
            f"📅 Period: {summary['start_date']} to {summary['end_date']} ({summary['period_days']} days)\n"
            f"💰 Total Cost: ${summary['total_cost_usd']:.4f}\n"
            f"📈 Average Daily Cost: ${summary['avg_daily_cost_usd']:.4f}\n"
            f"🔍 Total Queries: {summary['total_queries']:,}\n"
            f"📊 Average Query Cost: ${summary['avg_query_cost_usd']:.4f}",
            title="📋 Cost Overview",
            border_style="blue"
        )
        console.print(overview_panel)
        
        # Cost breakdown table
        breakdown_table = Table(title="💰 Cost Breakdown by Category")
        breakdown_table.add_column("Category", style="cyan")
        breakdown_table.add_column("Total Cost", style="green")
        breakdown_table.add_column("Percentage", style="yellow")
        
        for category, cost in summary['cost_breakdown'].items():
            percentage = (cost / summary['total_cost_usd'] * 100) if summary['total_cost_usd'] > 0 else 0
            breakdown_table.add_row(
                category.replace('_', ' ').title(),
                f"${cost:.4f}",
                f"{percentage:.1f}%"
            )
            
        console.print(breakdown_table)
        
        # Top expensive days
        expensive_table = Table(title="🔥 Top Expensive Days")
        expensive_table.add_column("Date", style="cyan")
        expensive_table.add_column("Cost", style="red")
        expensive_table.add_column("Queries", style="yellow")
        
        for day in summary['expensive_days']:
            expensive_table.add_row(
                day['date'],
                f"${day['cost']:.4f}",
                str(day['queries'])
            )
            
        console.print(expensive_table)
        
        # Budget utilization
        budget_panel = Panel(
            f"💳 Total Budget: ${summary['budget_utilization']['total_budget']:.4f}\n"
            f"💸 Total Used: ${summary['budget_utilization']['total_used']:.4f}\n"
            f"📊 Average Utilization: {summary['budget_utilization']['avg_utilization']:.1f}%",
            title="💳 Budget Utilization",
            border_style="green"
        )
        console.print(budget_panel)
        
        # Recent trends
        console.print("\n📈 Recent Cost Trends")
        console.print("-" * 40)
        trends = self.analyze_cost_trends(days)
        if trends:
            trend_table = Table()
            trend_table.add_column("Period", style="cyan")
            trend_table.add_column("Cost", style="green")
            trend_table.add_column("Change", style="yellow")
            trend_table.add_column("Trend", style="blue")
            
            for trend in trends[:5]:  # Show last 5 trends
                change_color = "red" if trend.trend_direction == "increasing" else "green"
                trend_table.add_row(
                    trend.period,
                    f"${trend.total_cost:.4f}",
                    f"{trend.cost_change_percent:+.1f}%",
                    f"[{change_color}]{trend.trend_direction}[/{change_color}]"
                )
                
            console.print(trend_table)
        else:
            console.print("   No trend data available")
            
        # Cost anomalies
        console.print("\n🚨 Recent Cost Anomalies")
        console.print("-" * 40)
        anomalies = self.detect_cost_anomalies(days)
        if anomalies:
            anomaly_table = Table()
            anomaly_table.add_column("Date", style="cyan")
            anomaly_table.add_column("Type", style="red")
            anomaly_table.add_column("Severity", style="yellow")
            anomaly_table.add_column("Description", style="white")
            
            for anomaly in anomalies[:5]:  # Show last 5 anomalies
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
                    anomaly.description[:50] + "..." if len(anomaly.description) > 50 else anomaly.description
                )
                
            console.print(anomaly_table)
        else:
            console.print("   ✅ No anomalies detected")
            
    def cleanup_old_records(self, days_to_keep: int = 365):
        """Clean up old cost history records"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        
        initial_count = len(self.cost_records)
        self.cost_records = [record for record in self.cost_records if record.date >= cutoff_date]
        final_count = len(self.cost_records)
        
        if initial_count > final_count:
            console.print(f"🧹 Cleaned up {initial_count - final_count} old cost history records")
            self.save_cost_history()
            
        # Clean up old analytics
        cutoff_timestamp = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        initial_trends = len(self.cost_trends)
        initial_anomalies = len(self.cost_anomalies)
        
        self.cost_trends = [trend for trend in self.cost_trends if trend.start_date >= cutoff_date]
        self.cost_anomalies = [anomaly for anomaly in self.cost_anomalies if anomaly.timestamp >= cutoff_timestamp]
        
        if initial_trends > len(self.cost_trends) or initial_anomalies > len(self.cost_anomalies):
            console.print(f"🧹 Cleaned up old analytics data")
            self.save_cost_analytics()

# Global instance
_cost_history = None

def get_cost_history() -> CostHistory:
    """Get global cost history instance"""
    global _cost_history
    if _cost_history is None:
        _cost_history = CostHistory()
    return _cost_history
