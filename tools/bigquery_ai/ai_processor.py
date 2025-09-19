"""
Core BigQuery AI processor module
"""
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from config import config
from cost_monitor import get_cost_monitor

console = Console()

class BigQueryAIProcessor:
    """Core processor for BigQuery AI operations"""
    
    def __init__(self):
        self.client = bigquery.Client(project=config.gcp_project_id)
        self.cost_monitor = get_cost_monitor()
        self.setup_demo_tables()
        
    def setup_demo_tables(self):
        """Setup demo tables for AI processing"""
        try:
            # Create dataset if it doesn't exist
            dataset_ref = self.client.dataset(config.gcp_dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
            except Exception:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = config.gcp_location
                self.client.create_dataset(dataset)
                console.print(f"✅ Created dataset: {config.gcp_dataset_id}")
                
            # Create demo threat reports table
            self.create_demo_threat_reports()
            
            # Create infrastructure object table
            if config.enable_multimodal:
                self.create_infrastructure_table()
                
        except Exception as e:
            console.print(f"⚠️  Warning: Could not setup demo tables: {e}")
            
    def create_demo_threat_reports(self):
        """Create demo threat reports table with realistic cybersecurity scenarios"""
        table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports"
        
        schema = [
            bigquery.SchemaField("report_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("vendor_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("threat_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("severity", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("affected_systems", "STRING", mode="REPEATED"),
            bigquery.SchemaField("indicators", "STRING", mode="REPEATED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("raw_report", "STRING", mode="REQUIRED")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            self.client.get_table(table)
            console.print(f"✅ Demo threat reports table already exists")
        except Exception:
            self.client.create_table(table)
            console.print(f"✅ Created demo threat reports table")
            
            # Insert sample data
            self.insert_demo_threat_data()
            
    def create_infrastructure_table(self):
        """Create infrastructure object table for multimodal analysis"""
        table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects"
        
        schema = [
            bigquery.SchemaField("object_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("object_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("vendor_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("location", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("coordinates", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("risk_score", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("last_updated", "TIMESTAMP", mode="REQUIRED")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            self.client.get_table(table)
            console.print(f"✅ Infrastructure objects table already exists")
        except Exception:
            self.client.create_table(table)
            console.print(f"✅ Created infrastructure objects table")
            
            # Insert sample infrastructure data
            self.insert_demo_infrastructure_data()
            
    def insert_demo_threat_data(self):
        """Insert realistic demo threat data"""
        demo_data = [
            {
                "report_id": "RPT001",
                "timestamp": "2024-01-15T14:30:00Z",
                "vendor_name": "TechCorp Solutions",
                "threat_type": "supply-chain-compromise",
                "severity": 9,
                "description": "Suspicious network activity detected from compromised third-party software update server",
                "affected_systems": ["web-servers", "database-servers", "load-balancers"],
                "indicators": ["192.168.1.100:443", "update_service.exe", "unusual-network-patterns"],
                "status": "active",
                "raw_report": "Critical security alert: Our monitoring systems have detected anomalous network traffic patterns originating from what appears to be a compromised software update server operated by TechCorp Solutions. Multiple systems are showing signs of unauthorized access attempts and potential data exfiltration activities. The threat appears to be sophisticated and may involve advanced persistent threat actors targeting our supply chain infrastructure."
            },
            {
                "report_id": "RPT002",
                "timestamp": "2024-01-15T13:15:00Z",
                "vendor_name": "DataSystems Inc",
                "threat_type": "unauthorized-access",
                "severity": 7,
                "description": "Multiple failed login attempts followed by successful access from unknown IP addresses",
                "affected_systems": ["user-portal", "admin-console", "data-warehouse"],
                "indicators": ["203.0.113.0/24", "brute-force-pattern", "unusual-access-times"],
                "status": "investigating",
                "raw_report": "Security incident report: Our authentication systems have logged multiple failed login attempts followed by successful access from previously unknown IP address ranges. The successful logins occurred during unusual hours and accessed sensitive administrative functions. We suspect this may be a credential stuffing attack or targeted breach attempt."
            },
            {
                "report_id": "RPT003",
                "timestamp": "2024-01-15T12:45:00Z",
                "vendor_name": "CloudVendor Pro",
                "threat_type": "supply-chain-compromise",
                "severity": 8,
                "description": "Malicious code injection detected in cloud infrastructure deployment pipeline",
                "affected_systems": ["deployment-pipeline", "container-registry", "kubernetes-clusters"],
                "indicators": ["malicious-docker-image", "suspicious-deployment-script", "unauthorized-registry-access"],
                "status": "active",
                "raw_report": "Critical infrastructure alert: Our automated security scanning has detected malicious code within our cloud deployment pipeline. The compromised components appear to have been introduced through a supply chain attack targeting our third-party cloud infrastructure provider. Immediate containment measures have been implemented."
            }
        ]
        
        table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, demo_data)
        if errors:
            console.print(f"⚠️  Warning: Some demo data could not be inserted: {errors}")
        else:
            console.print(f"✅ Inserted {len(demo_data)} demo threat reports")
            
    def insert_demo_infrastructure_data(self):
        """Insert demo infrastructure data for multimodal analysis"""
        demo_data = [
            {
                "object_id": "INF001",
                "object_type": "data-center",
                "vendor_id": "V001",
                "location": "San Francisco, CA",
                "coordinates": "37.7749,-122.4194",
                "image_url": "https://example.com/datacenter-sf.jpg",
                "description": "Primary data center facility with redundant power and cooling systems",
                "risk_score": 0.85,
                "last_updated": "2024-01-15T10:00:00Z"
            },
            {
                "object_id": "INF002",
                "object_type": "network-hub",
                "vendor_id": "V002",
                "location": "Chicago, IL",
                "coordinates": "41.8781,-87.6298",
                "image_url": "https://example.com/network-hub-chicago.jpg",
                "description": "Regional network hub connecting multiple vendor systems",
                "risk_score": 0.72,
                "last_updated": "2024-01-15T09:00:00Z"
            }
        ]
        
        table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects"
        table = self.client.get_table(table_id)
        
        errors = self.client.insert_rows_json(table, demo_data)
        if errors:
            console.print(f"⚠️  Warning: Some infrastructure data could not be inserted: {errors}")
        else:
            console.print(f"✅ Inserted {len(demo_data)} infrastructure objects")
            
    def execute_ai_query(self, query: str, query_type: str = "ai_analysis") -> Tuple[bool, Any, float]:
        """Execute a BigQuery AI query with cost monitoring"""
        try:
            # Estimate cost before execution
            estimated_cost = self.cost_monitor.estimate_query_cost(query)
            
            # Check if query can be executed within budget
            can_execute, message = self.cost_monitor.can_execute_query(estimated_cost)
            if not can_execute:
                return False, {"error": message, "estimated_cost": estimated_cost}, 0.0
                
            console.print(f"💰 Estimated cost: ${estimated_cost:.4f}")
            
            # Execute query with timeout
            job_config = QueryJobConfig(
                timeout_ms=config.query_timeout_seconds * 1000,
                maximum_bytes_billed=config.max_processing_mb * 1024 * 1024
            )
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Executing {query_type}...", total=None)
                
                job = self.client.query(query, job_config=job_config)
                results = job.result()
                
                progress.update(task, description=f"Processing {query_type} results...")
                
                # Convert results to list of dictionaries
                data = []
                for row in results:
                    data.append(dict(row.items()))
                    
            # Calculate actual cost
            actual_cost = self.cost_monitor.estimate_query_cost(query)
            self.cost_monitor.add_query_cost(query, actual_cost, query_type)
            
            return True, data, actual_cost
            
        except Exception as e:
            console.print(f"❌ Error executing AI query: {e}")
            return False, {"error": str(e)}, 0.0
            
    def generate_threat_indicators(self, report_id: str) -> Dict:
        """Use AI.GENERATE_TABLE to extract structured threat indicators"""
        query = f"""
        SELECT 
            AI.GENERATE_TABLE(
                'Extract structured threat indicators from this security report. Return a table with columns: indicator_type, indicator_value, confidence_score, threat_level',
                raw_report,
                'gemini-1.5-flash'
            ) as threat_indicators
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        WHERE report_id = '{report_id}'
        LIMIT 1
        """
        
        success, results, cost = self.execute_ai_query(query, "threat_indicators_extraction")
        if success and results:
            return {
                "success": True,
                "data": results[0],
                "cost_usd": cost,
                "query_type": "AI.GENERATE_TABLE"
            }
        else:
            return {
                "success": False,
                "error": results.get("error", "Unknown error"),
                "cost_usd": cost
            }
            
    def generate_executive_briefing(self, vendor_name: str) -> Dict:
        """Use AI.GENERATE_TEXT to create executive security briefings"""
        query = f"""
        SELECT 
            AI.GENERATE_TEXT(
                'Create a concise executive security briefing for this vendor. Include: threat summary, risk assessment, recommended actions, and business impact. Format as bullet points.',
                CONCAT('Vendor: ', vendor_name, '. Recent threats: ', STRING_AGG(description, '; ')),
                'gemini-1.5-flash',
                1000
            ) as executive_briefing
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        WHERE vendor_name = '{vendor_name}'
        GROUP BY vendor_name
        """
        
        success, results, cost = self.execute_ai_query(query, "executive_briefing_generation")
        if success and results:
            return {
                "success": True,
                "data": results[0],
                "cost_usd": cost,
                "query_type": "AI.GENERATE_TEXT"
            }
        else:
            return {
                "success": False,
                "error": results.get("error", "Unknown error"),
                "cost_usd": cost
            }
            
    def generate_risk_scoring(self, vendor_name: str) -> Dict:
        """Use AI.GENERATE_DOUBLE for quantitative risk scoring"""
        query = f"""
        SELECT 
            AI.GENERATE_DOUBLE(
                'Based on the threat reports, generate a quantitative risk score from 0.0 to 1.0 where 1.0 is extremely high risk. Consider severity, frequency, and impact.',
                CONCAT('Vendor: ', vendor_name, '. Threats: ', STRING_AGG(CONCAT(threat_type, ' (', severity, ')'), '; ')),
                'gemini-1.5-flash'
            ) as risk_score
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        WHERE vendor_name = '{vendor_name}'
        GROUP BY vendor_name
        """
        
        success, results, cost = self.execute_ai_query(query, "risk_score_generation")
        if success and results:
            return {
                "success": True,
                "data": results[0],
                "cost_usd": cost,
                "query_type": "AI.GENERATE_DOUBLE"
            }
        else:
            return {
                "success": False,
                "error": results.get("error", "Unknown error"),
                "cost_usd": cost
            }
            
    def generate_threat_prediction(self, days_ahead: int = 30) -> Dict:
        """Use AI.FORECAST for threat prediction analysis"""
        query = f"""
        SELECT 
            AI.FORECAST(
                'Predict the number of high-severity threats (severity >= 7) for the next {days_ahead} days based on historical patterns.',
                ARRAY_AGG(severity ORDER BY timestamp),
                {days_ahead},
                'gemini-1.5-flash'
            ) as threat_prediction
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        WHERE severity >= 7
        """
        
        success, results, cost = self.execute_ai_query(query, "threat_prediction_forecast")
        if success and results:
            return {
                "success": True,
                "data": results[0],
                "cost_usd": cost,
                "query_type": "AI.FORECAST"
            }
        else:
            return {
                "success": False,
                "error": results.get("error", "Unknown error"),
                "cost_usd": cost
            }
            
    def get_processing_status(self) -> Dict:
        """Get current processing status and cost information"""
        cost_summary = self.cost_monitor.get_cost_summary()
        
        return {
            "status": "operational",
            "cost_summary": cost_summary,
            "budget_status": self.cost_monitor.get_budget_status(),
            "config": {
                "daily_budget_limit": config.daily_budget_limit_usd,
                "max_query_cost": config.max_query_cost_usd,
                "max_processing_mb": config.max_processing_mb,
                "query_timeout": config.query_timeout_seconds
            }
        }

    def generate_comprehensive_ai_analysis(self, report_id: str) -> Dict:
        """Generate comprehensive AI analysis using all available AI functions"""
        try:
            query = f"""
            WITH threat_data AS (
                SELECT 
                    report_id,
                    vendor_name,
                    threat_type,
                    severity,
                    description,
                    raw_report,
                    timestamp
                FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
                WHERE report_id = '{report_id}'
                LIMIT 1
            ),
            ai_analysis AS (
                SELECT 
                    -- AI.GENERATE_TEXT for comprehensive analysis
                    AI.GENERATE_TEXT(
                        'Generate a detailed supply chain threat analysis including risk factors, potential impact, and mitigation strategies.',
                        CONCAT('Threat Type: ', threat_type, ' | Vendor: ', vendor_name, ' | Description: ', description),
                        'gemini-1.5-flash',
                        800
                    ) as comprehensive_analysis,
                    
                    -- AI.GENERATE_TABLE for structured threat indicators
                    AI.GENERATE_TABLE(
                        'Extract key threat indicators in a structured format',
                        CONCAT('Threat: ', description),
                        'gemini-1.5-flash',
                        [
                            STRUCT('indicator_type' as STRING, 'description' as STRING, 'severity' as STRING, 'confidence' as FLOAT64)
                        ]
                    ) as threat_indicators,
                    
                    -- AI.GENERATE_BOOL for critical threat assessment
                    AI.GENERATE_BOOL(
                        'Is this threat critical enough to require immediate attention? Consider severity, vendor importance, and potential supply chain impact.',
                        CONCAT('Threat: ', description, ' | Severity: ', CAST(severity AS STRING))
                    ) as requires_immediate_attention,
                    
                    -- AI.GENERATE_INT for threat priority score
                    AI.GENERATE_INT(
                        'Generate a threat priority score from 1-10 where 10 is highest priority. Consider severity, vendor criticality, and supply chain impact.',
                        CONCAT('Threat: ', description, ' | Vendor: ', vendor_name, ' | Severity: ', CAST(severity AS STRING))
                    ) as priority_score,
                    
                    -- AI.GENERATE_DOUBLE for risk assessment
                    AI.GENERATE_DOUBLE(
                        'Generate a risk score from 0.0 to 1.0 for this supply chain threat. Higher scores indicate higher risk.',
                        CONCAT('Threat: ', description, ' | Vendor: ', vendor_name, ' | Severity: ', CAST(severity AS STRING))
                    ) as risk_score,
                    
                    -- ML.GENERATE_TEXT for classic LLM generation
                    ML.GENERATE_TEXT(
                        'text-bison@001',
                        'Explain this supply chain vulnerability in simple terms for executive leadership',
                        description
                    ) as executive_summary,
                    
                    -- AI.FORECAST for threat trend prediction
                    AI.FORECAST(
                        'forecast_threat_trends',
                        ARRAY[severity],
                        timestamp,
                        30
                    ) as threat_trend_forecast
                    
                FROM threat_data
            )
            SELECT 
                report_id,
                comprehensive_analysis,
                threat_indicators,
                requires_immediate_attention,
                priority_score,
                risk_score,
                executive_summary,
                threat_trend_forecast
            FROM ai_analysis
            """
            
            success, results, cost = self.execute_ai_query(query, "comprehensive_ai_analysis")
            if success and results:
                return {
                    "success": True,
                    "data": results[0],
                    "cost_usd": cost,
                    "query_type": "Comprehensive AI Analysis with All Functions",
                    "ai_functions_used": [
                        "AI.GENERATE_TEXT",
                        "AI.GENERATE_TABLE", 
                        "AI.GENERATE_BOOL",
                        "AI.GENERATE_INT",
                        "AI.GENERATE_DOUBLE",
                        "ML.GENERATE_TEXT",
                        "AI.FORECAST"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": results.get("error", "Unknown error"),
                    "cost_usd": cost
                }
                
        except Exception as e:
            console.print(f"❌ Error in comprehensive AI analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "cost_usd": 0.0
            }

    def generate_threat_forecast(self, days: int = 30) -> Dict:
        """Generate threat forecasting using AI.FORECAST"""
        try:
            query = f"""
            WITH threat_metrics AS (
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as threat_count,
                    AVG(severity) as avg_severity,
                    COUNTIF(severity >= 8) as critical_threats
                FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
                GROUP BY DATE(timestamp)
                ORDER BY date
            ),
            forecast_data AS (
                SELECT 
                    ARRAY_AGG(threat_count ORDER BY date) as threat_counts,
                    ARRAY_AGG(avg_severity ORDER BY date) as severity_trends,
                    ARRAY_AGG(critical_threats ORDER BY date) as critical_trends
                FROM threat_metrics
            )
            SELECT 
                AI.FORECAST('forecast_threat_volume', threat_counts, CURRENT_DATE(), {days}) as predicted_threat_volume,
                AI.FORECAST('forecast_severity_trend', severity_trends, CURRENT_DATE(), {days}) as predicted_severity,
                AI.FORECAST('forecast_critical_threats', critical_trends, CURRENT_DATE(), {days}) as predicted_critical_threats
            FROM forecast_data
            """
            
            success, results, cost = self.execute_ai_query(query, "threat_forecasting")
            if success and results:
                return {
                    "success": True,
                    "data": results[0],
                    "cost_usd": cost,
                    "query_type": "AI.FORECAST Threat Prediction",
                    "forecast_days": days
                }
            else:
                return {
                    "success": False,
                    "error": results.get("error", "Unknown error"),
                    "cost_usd": cost
                }
                
        except Exception as e:
            console.print(f"❌ Error in threat forecasting: {e}")
            return {
                "success": False,
                "error": str(e),
                "cost_usd": 0.0
            }

    def generate_structured_threat_analysis(self, report_id: str) -> Dict:
        """Generate structured threat analysis using AI.GENERATE_TABLE with custom schema"""
        try:
            query = f"""
            SELECT 
                AI.GENERATE_TABLE(
                    'Analyze this supply chain threat and extract structured information',
                    CONCAT('Threat Report: ', raw_report),
                    'gemini-1.5-flash',
                    [
                        STRUCT('threat_category' as STRING, 'attack_vector' as STRING, 'potential_impact' as STRING, 'mitigation_priority' as STRING, 'estimated_time_to_resolve' as STRING, 'affected_systems' as STRING, 'risk_level' as STRING)
                    ]
                ) as structured_analysis
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
            WHERE report_id = '{report_id}'
            LIMIT 1
            """
            
            success, results, cost = self.execute_ai_query(query, "structured_threat_analysis")
            if success and results:
                return {
                    "success": True,
                    "data": results[0],
                    "cost_usd": cost,
                    "query_type": "AI.GENERATE_TABLE Structured Analysis"
                }
            else:
                return {
                    "success": False,
                    "error": results.get("error", "Unknown error"),
                    "cost_usd": cost
                }
                
        except Exception as e:
            console.print(f"❌ Error in structured threat analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "cost_usd": 0.0
            }

# Global AI processor instance
ai_processor = BigQueryAIProcessor()

def get_ai_processor() -> BigQueryAIProcessor:
    """Get global AI processor instance"""
    return ai_processor
