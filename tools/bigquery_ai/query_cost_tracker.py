#!/usr/bin/env python3
"""
Query Cost Tracker for BigQuery AI processing
Provides detailed per-query cost monitoring and analytics
"""
import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from google.cloud.bigquery import QueryJob, QueryJobConfig
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import config
from billing_service import get_billing_service

console = Console()

@dataclass
class QueryCostRecord:
    """Detailed record of a single query execution"""
    query_id: str
    timestamp: str
    query_type: str
    query_hash: str
    query_preview: str
    full_query: str
    
    # Cost information
    estimated_cost_usd: float
    actual_cost_usd: float
    cost_difference_usd: float
    
    # Performance metrics
    execution_time_ms: int
    bytes_processed: int
    slot_ms: int
    
    # Job status
    job_status: str
    error_message: Optional[str]
    
    # Metadata
    user_agent: Optional[str]
    location: str
    project_id: str
    
    # Cost breakdown
    data_processing_cost: float
    compute_slots_cost: float
    
    # Tags and categorization
    tags: List[str]
    priority: str  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryCostRecord':
        """Create from dictionary"""
        return cls(**data)

class QueryCostTracker:
    """Comprehensive query cost tracking and analytics"""
    
    def __init__(self):
        self.billing_service = get_billing_service()
        self.cost_records: List[QueryCostRecord] = []
        self.cost_history_file = "query_cost_history.json"
        self.load_cost_history()
        
    def load_cost_history(self):
        """Load query cost history from file"""
        try:
            if os.path.exists(self.cost_history_file):
                with open(self.cost_history_file, 'r') as f:
                    data = json.load(f)
                    self.cost_records = [QueryCostRecord.from_dict(record) for record in data]
                    console.print(f"✅ Loaded {len(self.cost_records)} query cost records")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load query cost history: {e}")
            
    def save_cost_history(self):
        """Save query cost history to file"""
        try:
            data = [record.to_dict() for record in self.cost_records]
            with open(self.cost_history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save query cost history: {e}")
            
    def generate_query_id(self, query: str, query_type: str) -> str:
        """Generate unique query ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"{query_type}_{timestamp}_{query_hash}"
        
    def generate_query_hash(self, query: str) -> str:
        """Generate hash for query deduplication"""
        return hashlib.sha256(query.encode()).hexdigest()
        
    def estimate_query_cost(self, query: str) -> Tuple[float, Dict[str, Any]]:
        """Estimate query cost using BigQuery dry-run"""
        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=config.gcp_project_id)
            
            job_config = QueryJobConfig(dry_run=True)
            job = client.query(query, job_config=job_config)
            
            # Calculate estimated costs
            bytes_processed = job.total_bytes_processed
            bytes_cost = (bytes_processed / (1024**4)) * 5.0  # $5 per TB
            
            # Estimate slot usage (conservative estimate)
            estimated_slots = 1000  # 1 slot-second
            slots_cost = (estimated_slots / (1000 * 3600)) * 0.01  # $0.01 per slot-hour
            
            total_cost = bytes_cost + slots_cost
            
            breakdown = {
                "bytes_processed": bytes_processed,
                "data_processing_cost": bytes_cost,
                "estimated_slots": estimated_slots,
                "compute_slots_cost": slots_cost,
                "total_cost": total_cost
            }
            
            return total_cost, breakdown
            
        except Exception as e:
            console.print(f"⚠️  Warning: Could not estimate query cost: {e}")
            return 0.0, {"error": str(e)}
            
    def track_query_execution(self, 
                            query: str, 
                            query_type: str,
                            job: Optional[QueryJob] = None,
                            execution_time_ms: int = 0,
                            error_message: Optional[str] = None) -> QueryCostRecord:
        """Track a complete query execution"""
        try:
            # Generate unique identifiers
            query_id = self.generate_query_id(query, query_type)
            query_hash = self.generate_query_hash(query)
            query_preview = query[:100] + "..." if len(query) > 100 else query
            
            # Estimate costs
            estimated_cost, cost_breakdown = self.estimate_query_cost(query)
            
            # Get actual costs if job is available
            actual_cost = estimated_cost
            actual_bytes = cost_breakdown.get("bytes_processed", 0)
            actual_slots = cost_breakdown.get("estimated_slots", 0)
            
            if job and hasattr(job, 'total_bytes_processed'):
                actual_bytes = job.total_bytes_processed
                actual_cost = (actual_bytes / (1024**4)) * 5.0
                
            if job and hasattr(job, 'total_slot_ms'):
                actual_slots = job.total_slot_ms
                slots_cost = (actual_slots / (1000 * 3600)) * 0.01
                actual_cost += slots_cost
                
            # Calculate cost difference
            cost_difference = actual_cost - estimated_cost
            
            # Determine priority based on cost
            if actual_cost > config.max_query_cost_usd:
                priority = "critical"
            elif actual_cost > config.max_query_cost_usd * 0.5:
                priority = "high"
            elif actual_cost > config.max_query_cost_usd * 0.2:
                priority = "medium"
            else:
                priority = "low"
                
            # Create cost record
            record = QueryCostRecord(
                query_id=query_id,
                timestamp=datetime.now().isoformat(),
                query_type=query_type,
                query_hash=query_hash,
                query_preview=query_preview,
                full_query=query,
                estimated_cost_usd=estimated_cost,
                actual_cost_usd=actual_cost,
                cost_difference_usd=cost_difference,
                execution_time_ms=execution_time_ms,
                bytes_processed=actual_bytes,
                slot_ms=actual_slots,
                job_status="DONE" if not error_message else "ERROR",
                error_message=error_message,
                user_agent="BigQuery-AI-Processor",
                location=config.gcp_location,
                project_id=config.gcp_project_id,
                data_processing_cost=(actual_bytes / (1024**4)) * 5.0,
                compute_slots_cost=(actual_slots / (1000 * 3600)) * 0.01,
                tags=[query_type, priority, f"cost_{'high' if actual_cost > 1.0 else 'medium' if actual_cost > 0.1 else 'low'}"],
                priority=priority
            )
            
            # Store record
            self.cost_records.append(record)
            self.save_cost_history()
            
            console.print(f"💰 Query cost tracked: ${actual_cost:.4f} ({query_type})")
            return record
            
        except Exception as e:
            console.print(f"❌ Error tracking query execution: {e}")
            # Return minimal record on error
            return QueryCostRecord(
                query_id="error",
                timestamp=datetime.now().isoformat(),
                query_type=query_type,
                query_hash="",
                query_preview="",
                full_query=query,
                estimated_cost_usd=0.0,
                actual_cost_usd=0.0,
                cost_difference_usd=0.0,
                execution_time_ms=execution_time_ms,
                bytes_processed=0,
                slot_ms=0,
                job_status="ERROR",
                error_message=str(e),
                user_agent="BigQuery-AI-Processor",
                location=config.gcp_location,
                project_id=config.gcp_project_id,
                data_processing_cost=0.0,
                compute_slots_cost=0.0,
                tags=[query_type, "error"],
                priority="low"
            )
            
    def get_query_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive query cost summary"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in self.cost_records
                if datetime.fromisoformat(record.timestamp) > cutoff_date
            ]
            
            if not recent_records:
                return {"error": "No query records found for the specified period"}
                
            # Calculate totals
            total_queries = len(recent_records)
            total_cost = sum(record.actual_cost_usd for record in recent_records)
            total_estimated = sum(record.estimated_cost_usd for record in recent_records)
            total_difference = sum(record.cost_difference_usd for record in recent_records)
            
            # Cost breakdown by type
            cost_by_type = {}
            for record in recent_records:
                if record.query_type not in cost_by_type:
                    cost_by_type[record.query_type] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "avg_cost": 0.0
                    }
                cost_by_type[record.query_type]["count"] += 1
                cost_by_type[record.query_type]["total_cost"] += record.actual_cost_usd
                
            # Calculate averages
            for query_type in cost_by_type:
                count = cost_by_type[query_type]["count"]
                total = cost_by_type[query_type]["total_cost"]
                cost_by_type[query_type]["avg_cost"] = total / count if count > 0 else 0.0
                
            # Performance metrics
            avg_execution_time = sum(record.execution_time_ms for record in recent_records) / len(recent_records)
            total_bytes_processed = sum(record.bytes_processed for record in recent_records)
            
            # Priority breakdown
            priority_breakdown = {}
            for record in recent_records:
                if record.priority not in priority_breakdown:
                    priority_breakdown[record.priority] = {"count": 0, "total_cost": 0.0}
                priority_breakdown[record.priority]["count"] += 1
                priority_breakdown[record.priority]["total_cost"] += record.actual_cost_usd
                
            return {
                "period_days": days,
                "total_queries": total_queries,
                "total_cost_usd": total_cost,
                "total_estimated_usd": total_estimated,
                "cost_difference_usd": total_difference,
                "cost_accuracy_percent": ((total_estimated - total_difference) / total_estimated * 100) if total_estimated > 0 else 0,
                "avg_cost_per_query": total_cost / total_queries if total_queries > 0 else 0,
                "avg_execution_time_ms": avg_execution_time,
                "total_bytes_processed": total_bytes_processed,
                "cost_by_type": cost_by_type,
                "priority_breakdown": priority_breakdown,
                "cost_trends": self._calculate_cost_trends(recent_records),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            console.print(f"❌ Error getting query cost summary: {e}")
            return {"error": str(e)}
            
    def _calculate_cost_trends(self, records: List[QueryCostRecord]) -> Dict[str, Any]:
        """Calculate cost trends over time"""
        try:
            # Group by date
            daily_costs = {}
            for record in records:
                date = record.timestamp[:10]  # YYYY-MM-DD
                if date not in daily_costs:
                    daily_costs[date] = {"cost": 0.0, "count": 0}
                daily_costs[date]["cost"] += record.actual_cost_usd
                daily_costs[date]["count"] += 1
                
            # Sort by date
            sorted_dates = sorted(daily_costs.keys())
            
            # Calculate trends
            if len(sorted_dates) >= 2:
                first_date = sorted_dates[0]
                last_date = sorted_dates[-1]
                first_cost = daily_costs[first_date]["cost"]
                last_cost = daily_costs[last_date]["cost"]
                
                if first_cost > 0:
                    cost_change_percent = ((last_cost - first_cost) / first_cost) * 100
                else:
                    cost_change_percent = 0
                    
                trend = "increasing" if cost_change_percent > 5 else "decreasing" if cost_change_percent < -5 else "stable"
            else:
                cost_change_percent = 0
                trend = "stable"
                
            return {
                "daily_costs": daily_costs,
                "cost_change_percent": cost_change_percent,
                "trend": trend,
                "date_range": {"start": sorted_dates[0] if sorted_dates else None, "end": sorted_dates[-1] if sorted_dates else None}
            }
            
        except Exception as e:
            console.print(f"⚠️  Warning: Could not calculate cost trends: {e}")
            return {"error": str(e)}
            
    def get_daily_cost_breakdown(self, date: str) -> Dict[str, Any]:
        """Get detailed cost breakdown for a specific date"""
        # Filter records for the specified date
        date_records = [
            record for record in self.cost_records
            if record.timestamp.startswith(date)
        ]
        
        if not date_records:
            return {
                'total_cost': 0.0,
                'data_processing_cost': 0.0,
                'compute_slots_cost': 0.0,
                'storage_cost': 0.0,
                'network_cost': 0.0,
                'ai_models_cost': 0.0,
                'other_costs': 0.0,
                'bytes_processed': 0,
                'slot_ms': 0,
                'storage_bytes': 0,
                'network_bytes': 0,
                'total_queries': 0,
                'successful_queries': 0,
                'failed_queries': 0,
                'avg_query_cost': 0.0,
                'max_query_cost': 0.0,
                'tags': [],
                'cost_center': None
            }
            
        # Calculate totals
        total_cost = sum(record.estimated_cost_usd for record in date_records)
        total_queries = len(date_records)
        successful_queries = sum(1 for record in date_records if record.job_status == 'DONE')
        failed_queries = total_queries - successful_queries
        
        # Cost breakdown (simplified - in real implementation, these would come from detailed billing)
        data_processing_cost = sum(record.data_processing_cost for record in date_records)
        compute_slots_cost = sum(record.compute_slots_cost for record in date_records)
        storage_cost = 0.0  # Would come from storage billing
        network_cost = 0.0  # Would come from network billing
        ai_models_cost = 0.0  # Would come from AI model usage billing
        other_costs = total_cost - data_processing_cost - compute_slots_cost - storage_cost - network_cost - ai_models_cost
        
        # Usage metrics
        bytes_processed = sum(record.bytes_processed for record in date_records)
        slot_ms = sum(record.slot_ms for record in date_records)
        storage_bytes = 0  # Would come from storage metrics
        network_bytes = 0  # Would come from network metrics
        
        # Query metrics
        avg_query_cost = total_cost / total_queries if total_queries > 0 else 0.0
        max_query_cost = max(record.estimated_cost_usd for record in date_records) if date_records else 0.0
        
        # Tags and metadata
        all_tags = []
        for record in date_records:
            all_tags.extend(record.tags)
        unique_tags = list(set(all_tags))
        
        return {
            'total_cost': total_cost,
            'data_processing_cost': data_processing_cost,
            'compute_slots_cost': compute_slots_cost,
            'storage_cost': storage_cost,
            'network_cost': network_cost,
            'ai_models_cost': ai_models_cost,
            'other_costs': other_costs,
            'bytes_processed': bytes_processed,
            'slot_ms': slot_ms,
            'storage_bytes': storage_bytes,
            'network_bytes': network_bytes,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'avg_query_cost': avg_query_cost,
            'max_query_cost': max_query_cost,
            'tags': unique_tags,
            'cost_center': None  # Would come from project configuration
        }
            
    def get_expensive_queries(self, limit: int = 10, days: int = 30) -> List[QueryCostRecord]:
        """Get most expensive queries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in self.cost_records
                if datetime.fromisoformat(record.timestamp) > cutoff_date
            ]
            
            # Sort by cost (descending)
            sorted_records = sorted(recent_records, key=lambda x: x.actual_cost_usd, reverse=True)
            return sorted_records[:limit]
            
        except Exception as e:
            console.print(f"❌ Error getting expensive queries: {e}")
            return []
            
    def get_query_performance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get query performance metrics"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_records = [
                record for record in self.cost_records
                if datetime.fromisoformat(record.timestamp) > cutoff_date
            ]
            
            if not recent_records:
                return {"error": "No query records found for the specified period"}
                
            # Performance metrics
            execution_times = [record.execution_time_ms for record in recent_records]
            costs = [record.actual_cost_usd for record in recent_records]
            bytes_processed = [record.bytes_processed for record in recent_records]
            
            # Calculate statistics
            avg_execution_time = sum(execution_times) / len(execution_times)
            avg_cost = sum(costs) / len(costs)
            avg_bytes = sum(bytes_processed) / len(bytes_processed)
            
            # Find outliers
            cost_threshold = avg_cost * 2  # 2x average cost
            time_threshold = avg_execution_time * 2  # 2x average time
            
            outliers = [
                record for record in recent_records
                if record.actual_cost_usd > cost_threshold or record.execution_time_ms > time_threshold
            ]
            
            return {
                "total_queries": len(recent_records),
                "avg_execution_time_ms": avg_execution_time,
                "avg_cost_usd": avg_cost,
                "avg_bytes_processed": avg_bytes,
                "outliers_count": len(outliers),
                "outliers": [record.query_id for record in outliers],
                "performance_distribution": {
                    "fast_queries": len([t for t in execution_times if t < avg_execution_time * 0.5]),
                    "normal_queries": len([t for t in execution_times if avg_execution_time * 0.5 <= t <= avg_execution_time * 1.5]),
                    "slow_queries": len([t for t in execution_times if t > avg_execution_time * 1.5])
                },
                "cost_distribution": {
                    "low_cost": len([c for c in costs if c < avg_cost * 0.5]),
                    "normal_cost": len([c for c in costs if avg_cost * 0.5 <= c <= avg_cost * 1.5]),
                    "high_cost": len([c for c in costs if c > avg_cost * 1.5])
                }
            }
            
        except Exception as e:
            console.print(f"❌ Error getting performance metrics: {e}")
            return {"error": str(e)}
            
    def display_query_cost_dashboard(self, days: int = 30):
        """Display comprehensive query cost dashboard"""
        try:
            console.print(f"\n📊 Query Cost Dashboard (Last {days} days)")
            console.print("=" * 60)
            
            # Get summary
            summary = self.get_query_cost_summary(days)
            if "error" in summary:
                console.print(f"❌ Error: {summary['error']}")
                return
                
            # Cost overview
            cost_text = Text()
            cost_text.append(f"Total Queries: {summary['total_queries']}\n", style="bold blue")
            cost_text.append(f"Total Cost: ${summary['total_cost_usd']:.4f}\n", style="bold green")
            cost_text.append(f"Avg Cost/Query: ${summary['avg_cost_per_query']:.4f}\n", style="bold yellow")
            cost_text.append(f"Cost Accuracy: {summary['cost_accuracy_percent']:.1f}%\n", style="bold magenta")
            cost_text.append(f"Avg Execution Time: {summary['avg_execution_time_ms']:.0f}ms", style="bold cyan")
            
            cost_panel = Panel(cost_text, title="💰 Cost Overview", border_style="blue")
            console.print(cost_panel)
            
            # Cost by query type
            if summary['cost_by_type']:
                type_table = Table(title="📊 Cost by Query Type")
                type_table.add_column("Type", style="cyan")
                type_table.add_column("Count", style="magenta")
                type_table.add_column("Total Cost", style="green")
                type_table.add_column("Avg Cost", style="yellow")
                
                for query_type, data in summary['cost_by_type'].items():
                    type_table.add_row(
                        query_type,
                        str(data['count']),
                        f"${data['total_cost']:.4f}",
                        f"${data['avg_cost']:.4f}"
                    )
                    
                console.print(type_table)
                
            # Priority breakdown
            if summary['priority_breakdown']:
                priority_table = Table(title="🚨 Priority Breakdown")
                priority_table.add_column("Priority", style="cyan")
                priority_table.add_column("Count", style="magenta")
                priority_table.add_column("Total Cost", style="green")
                
                for priority, data in summary['priority_breakdown'].items():
                    priority_color = "red" if priority == "critical" else "yellow" if priority == "high" else "green"
                    priority_table.add_row(
                        f"[bold {priority_color}]{priority}[/bold {priority_color}]",
                        str(data['count']),
                        f"${data['total_cost']:.4f}"
                    )
                    
                console.print(priority_table)
                
            # Cost trends
            if 'cost_trends' in summary and 'error' not in summary['cost_trends']:
                trends = summary['cost_trends']
                trend_text = Text()
                trend_text.append(f"Trend: {trends['trend'].title()}\n", style="bold blue")
                trend_text.append(f"Cost Change: {trends['cost_change_percent']:+.1f}%\n", style="bold green")
                if trends['date_range']['start'] and trends['date_range']['end']:
                    trend_text.append(f"Period: {trends['date_range']['start']} to {trends['date_range']['end']}", style="bold yellow")
                    
                trend_panel = Panel(trend_text, title="📈 Cost Trends", border_style="green")
                console.print(trend_panel)
                
            # Most expensive queries
            expensive_queries = self.get_expensive_queries(limit=5, days=days)
            if expensive_queries:
                console.print("\n💸 Most Expensive Queries")
                console.print("=" * 40)
                
                for i, record in enumerate(expensive_queries, 1):
                    console.print(f"{i}. {record.query_type} - ${record.actual_cost_usd:.4f}")
                    console.print(f"   {record.query_preview}")
                    console.print(f"   Executed: {record.timestamp[:19]}")
                    console.print()
                    
        except Exception as e:
            console.print(f"❌ Error displaying query cost dashboard: {e}")
            
    def cleanup_old_records(self, days_to_keep: int = 90):
        """Clean up old query cost records"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            original_count = len(self.cost_records)
            
            self.cost_records = [
                record for record in self.cost_records
                if datetime.fromisoformat(record.timestamp) > cutoff_date
            ]
            
            removed_count = original_count - len(self.cost_records)
            if removed_count > 0:
                self.save_cost_history()
                console.print(f"🧹 Cleaned up {removed_count} old query cost records")
                
        except Exception as e:
            console.print(f"❌ Error cleaning up old records: {e}")

# Global query cost tracker instance
query_cost_tracker = QueryCostTracker()

def get_query_cost_tracker() -> QueryCostTracker:
    """Get global query cost tracker instance"""
    return query_cost_tracker
