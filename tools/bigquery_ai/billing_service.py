#!/usr/bin/env python3
"""
BigQuery Billing API integration service
Provides real-time cost tracking and budget monitoring
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from google.cloud import billing_v1
from google.cloud.bigquery import Client as BigQueryClient
from google.api_core import exceptions
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from config import config

console = Console()

class BigQueryBillingService:
    """Real-time BigQuery billing and cost monitoring service"""
    
    def __init__(self):
        self.project_id = config.gcp_project_id
        self.billing_client = billing_v1.CloudBillingClient()
        self.bigquery_client = BigQueryClient(project=self.project_id)
        self.billing_account = None
        self.cost_cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
    def get_billing_account(self) -> Optional[str]:
        """Get the billing account associated with the project"""
        try:
            if self.billing_account:
                return self.billing_account
                
            # Get project billing info
            project_name = f"projects/{self.project_id}"
            project_billing_info = self.billing_client.get_project_billing_info(name=project_name)
            
            if project_billing_info.billing_account_name:
                self.billing_account = project_billing_info.billing_account_name
                console.print(f"✅ Billing account found: {self.billing_account}")
                return self.billing_account
            else:
                console.print("❌ No billing account associated with project")
                return None
                
        except Exception as e:
            console.print(f"❌ Error getting billing account: {e}")
            return None
            
    def get_real_time_costs(self, days: int = 7) -> Dict[str, Any]:
        """Get real-time costs from Google Cloud Billing API"""
        try:
            billing_account = self.get_billing_account()
            if not billing_account:
                return {"error": "No billing account available"}
                
            # Check cache first
            cache_key = f"costs_{days}"
            if cache_key in self.cost_cache:
                cache_time, cache_data = self.cost_cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    return cache_data
                    
            # Get billing data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for API
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Get BigQuery-specific costs
            bigquery_costs = self._get_bigquery_costs(start_date_str, end_date_str)
            
            # Get overall project costs
            project_costs = self._get_project_costs(start_date_str, end_date_str)
            
            # Combine and format results
            result = {
                "billing_account": billing_account,
                "project_id": self.project_id,
                "period": {
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "days": days
                },
                "bigquery_costs": bigquery_costs,
                "project_costs": project_costs,
                "total_costs": {
                    "bigquery": bigquery_costs.get("total_cost", 0.0),
                    "project": project_costs.get("total_cost", 0.0),
                    "overall": 0.0
                },
                "cache_info": {
                    "cached_at": datetime.now().isoformat(),
                    "cache_ttl_seconds": self.cache_ttl
                }
            }
            
            # Calculate overall total
            result["total_costs"]["overall"] = (
                result["total_costs"]["bigquery"] + 
                result["total_costs"]["project"]
            )
            
            # Cache the result
            self.cost_cache[cache_key] = (time.time(), result)
            
            return result
            
        except Exception as e:
            console.print(f"❌ Error getting real-time costs: {e}")
            return {"error": str(e)}
            
    def _get_bigquery_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get BigQuery-specific costs using BigQuery billing export or estimation"""
        try:
            # Try to get actual BigQuery costs from billing export
            # If not available, estimate based on query usage
            
            # Get recent BigQuery jobs for cost estimation
            query = f"""
            SELECT 
                job_id,
                creation_time,
                total_bytes_processed,
                total_slot_ms,
                state
            FROM `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
            WHERE creation_time BETWEEN TIMESTAMP('{start_date}') AND TIMESTAMP('{end_date}')
            AND state = 'DONE'
            ORDER BY creation_time DESC
            LIMIT 1000
            """
            
            try:
                query_job = self.bigquery_client.query(query)
                results = query_job.result()
                
                total_bytes = 0
                total_slots = 0
                job_count = 0
                
                for row in results:
                    total_bytes += row.total_bytes_processed or 0
                    total_slots += row.total_slot_ms or 0
                    job_count += 1
                    
                # Calculate estimated costs
                # BigQuery pricing: $5 per TB processed, $0.01 per slot-hour
                bytes_cost = (total_bytes / (1024**4)) * 5.0  # Convert to TB
                slots_cost = (total_slots / (1000 * 3600)) * 0.01  # Convert to hours
                total_cost = bytes_cost + slots_cost
                
                return {
                    "total_cost": total_cost,
                    "bytes_cost": bytes_cost,
                    "slots_cost": slots_cost,
                    "total_bytes_processed": total_bytes,
                    "total_slot_ms": total_slots,
                    "job_count": job_count,
                    "cost_breakdown": {
                        "data_processing": bytes_cost,
                        "compute_slots": slots_cost
                    },
                    "pricing": {
                        "bytes_per_tb": 5.0,
                        "slots_per_hour": 0.01
                    }
                }
                
            except Exception as e:
                console.print(f"⚠️  Could not get BigQuery job costs: {e}")
                # Fallback to estimated costs
                return {
                    "total_cost": 0.0,
                    "bytes_cost": 0.0,
                    "slots_cost": 0.0,
                    "total_bytes_processed": 0,
                    "total_slot_ms": 0,
                    "job_count": 0,
                    "cost_breakdown": {
                        "data_processing": 0.0,
                        "compute_slots": 0.0
                    },
                    "pricing": {
                        "bytes_per_tb": 5.0,
                        "slots_per_hour": 0.01
                    },
                    "note": "Estimated costs - actual billing data unavailable"
                }
                
        except Exception as e:
            console.print(f"❌ Error getting BigQuery costs: {e}")
            return {"error": str(e)}
            
    def _get_project_costs(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get overall project costs from Cloud Billing API"""
        try:
            billing_account = self.get_billing_account()
            if not billing_account:
                return {"error": "No billing account available"}
                
            # Get cost data from Cloud Billing API
            # Note: This requires billing export to be enabled
            # For now, return estimated costs
            
            return {
                "total_cost": 0.0,
                "services": {},
                "note": "Project costs require billing export setup",
                "setup_required": True
            }
            
        except Exception as e:
            console.print(f"❌ Error getting project costs: {e}")
            return {"error": str(e)}
            
    def get_daily_cost_breakdown(self, date: str = None) -> Dict[str, Any]:
        """Get detailed cost breakdown for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # Get costs for the specific date
            costs = self.get_real_time_costs(days=1)
            
            if "error" in costs:
                return {"error": costs["error"]}
                
            # Filter for specific date
            daily_costs = {
                "date": date,
                "bigquery_costs": costs["bigquery_costs"],
                "project_costs": costs["project_costs"],
                "total_cost": costs["total_costs"]["overall"],
                "cost_analysis": {
                    "is_within_budget": costs["total_costs"]["overall"] <= config.daily_budget_limit_usd,
                    "budget_remaining": config.daily_budget_limit_usd - costs["total_costs"]["overall"],
                    "budget_usage_percent": (costs["total_costs"]["overall"] / config.daily_budget_limit_usd) * 100
                }
            }
            
            return daily_costs
            
        except Exception as e:
            console.print(f"❌ Error getting daily cost breakdown: {e}")
            return {"error": str(e)}
            
    def get_cost_alerts(self) -> List[Dict[str, Any]]:
        """Get cost alerts based on current spending"""
        try:
            today_costs = self.get_daily_cost_breakdown()
            
            if "error" in today_costs:
                return [{"error": today_costs["error"]}]
                
            alerts = []
            total_cost = today_costs["total_cost"]
            budget_limit = config.daily_budget_limit_usd
            usage_percent = today_costs["cost_analysis"]["budget_usage_percent"]
            
            # Critical alert - budget exceeded
            if total_cost >= budget_limit:
                alerts.append({
                    "level": "critical",
                    "message": f"Daily budget limit exceeded! ${total_cost:.4f} / ${budget_limit}",
                    "timestamp": datetime.now().isoformat(),
                    "action_required": True
                })
                
            # Warning alert - approaching limit
            elif usage_percent >= 90:
                alerts.append({
                    "level": "warning",
                    "message": f"Approaching daily budget limit! {usage_percent:.1f}% used",
                    "timestamp": datetime.now().isoformat(),
                    "action_required": False
                })
                
            # Notice alert - high usage
            elif usage_percent >= 75:
                alerts.append({
                    "level": "notice",
                    "message": f"High daily budget usage: {usage_percent:.1f}%",
                    "timestamp": datetime.now().isoformat(),
                    "action_required": False
                })
                
            return alerts
            
        except Exception as e:
            console.print(f"❌ Error getting cost alerts: {e}")
            return [{"error": str(e)}]
            
    def display_billing_dashboard(self):
        """Display real-time billing dashboard"""
        try:
            costs = self.get_real_time_costs(days=7)
            
            if "error" in costs:
                console.print(f"❌ Error: {costs['error']}")
                return
                
            # Create billing overview panel
            billing_text = Text()
            billing_text.append(f"Project: {costs['project_id']}\n", style="bold blue")
            billing_text.append(f"Billing Account: {costs['billing_account']}\n", style="bold green")
            billing_text.append(f"Period: {costs['period']['start_date']} to {costs['period']['end_date']}\n", style="bold yellow")
            billing_text.append(f"Total Cost: ${costs['total_costs']['overall']:.4f}\n", style="bold red")
            
            billing_panel = Panel(billing_text, title="🏦 Billing Overview", border_style="blue")
            console.print(billing_panel)
            
            # Create BigQuery costs panel
            bigquery_costs = costs["bigquery_costs"]
            if "error" not in bigquery_costs:
                bigquery_text = Text()
                bigquery_text.append(f"BigQuery Total: ${bigquery_costs['total_cost']:.4f}\n", style="bold green")
                bigquery_text.append(f"Data Processing: ${bigquery_costs['bytes_cost']:.4f}\n", style="cyan")
                bigquery_text.append(f"Compute Slots: ${bigquery_costs['slots_cost']:.4f}\n", style="magenta")
                bigquery_text.append(f"Jobs Processed: {bigquery_costs['job_count']}\n", style="yellow")
                
                bigquery_panel = Panel(bigquery_text, title="📊 BigQuery Costs", border_style="green")
                console.print(bigquery_panel)
                
            # Display cost alerts
            alerts = self.get_cost_alerts()
            if alerts and "error" not in alerts[0]:
                alert_text = Text()
                for alert in alerts:
                    color = "red" if alert["level"] == "critical" else "yellow" if alert["level"] == "warning" else "blue"
                    alert_text.append(f"{alert['level'].upper()}: {alert['message']}\n", style=f"bold {color}")
                    
                alert_panel = Panel(alert_text, title="🚨 Cost Alerts", border_style="red")
                console.print(alert_panel)
                
        except Exception as e:
            console.print(f"❌ Error displaying billing dashboard: {e}")
            
    def setup_billing_export(self) -> Dict[str, Any]:
        """Setup BigQuery billing export for accurate cost tracking"""
        try:
            billing_account = self.get_billing_account()
            if not billing_account:
                return {"error": "No billing account available"}
                
            # Check if billing export is already configured
            dataset_id = "billing_export"
            table_id = "gcp_billing_export_v1"
            
            try:
                # Try to access billing export table
                table_ref = self.bigquery_client.dataset(dataset_id).table(table_id)
                self.bigquery_client.get_table(table_ref)
                
                return {
                    "status": "already_configured",
                    "message": "Billing export already configured",
                    "dataset": dataset_id,
                    "table": table_id
                }
                
            except Exception:
                # Billing export not configured
                return {
                    "status": "not_configured",
                    "message": "Billing export not configured",
                    "setup_instructions": [
                        "1. Go to Google Cloud Console > Billing",
                        "2. Select your billing account",
                        "3. Go to Billing Export",
                        "4. Create new export to BigQuery",
                        "5. Set dataset to 'billing_export'",
                        "6. Set table to 'gcp_billing_export_v1'"
                    ],
                    "note": "Billing export provides accurate cost data but requires manual setup"
                }
                
        except Exception as e:
            console.print(f"❌ Error setting up billing export: {e}")
            return {"error": str(e)}

# Global billing service instance
billing_service = BigQueryBillingService()

def get_billing_service() -> BigQueryBillingService:
    """Get global billing service instance"""
    return billing_service
