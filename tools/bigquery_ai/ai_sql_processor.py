"""
AI SQL Processor - Implements all Google SQL AI functions for supply chain threat analysis
"""
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import config
from cost_monitor import get_cost_monitor

console = Console()

class AISQLProcessor:
    """Comprehensive AI SQL processor implementing all Google SQL AI functions"""
    
    def __init__(self):
        self.client = bigquery.Client(project=config.gcp_project_id)
        self.cost_monitor = get_cost_monitor()
        
    def generate_threat_summary(self, threat_description: str) -> Dict[str, Any]:
        """Generate threat summary using AI.GENERATE_TEXT"""
        query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Generate a comprehensive supply chain threat summary including risk level, affected components, and mitigation steps.',
                '{threat_description}'
            ) AS threat_summary,
            AI.GENERATE_TEXT(
                'Classify this threat as LOW, MEDIUM, HIGH, or CRITICAL based on supply chain impact.',
                '{threat_description}'
            ) AS risk_classification,
            AI.GENERATE_TEXT(
                'List the top 3 most critical supply chain components affected by this threat.',
                '{threat_description}'
            ) AS affected_components
        """
        
        return self._execute_ai_query(query, "threat_summary_generation")
    
    def forecast_threat_metrics(self, days_ahead: int = 60) -> Dict[str, Any]:
        """Forecast threat metrics using AI.FORECAST"""
        query = f"""
        WITH threat_metrics AS (
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as threat_count,
                AVG(CAST(severity AS FLOAT64)) as avg_severity,
                COUNTIF(severity >= 8) as critical_threats
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            GROUP BY DATE(timestamp)
            ORDER BY date
        )
        SELECT
            AI.FORECAST(
                'threat_count',
                threat_metrics,
                DATE_ADD(CURRENT_DATE(), INTERVAL {days_ahead} DAY),
                {days_ahead}
            ) AS forecasted_threats,
            AI.FORECAST(
                'avg_severity',
                threat_metrics,
                DATE_ADD(CURRENT_DATE(), INTERVAL {days_ahead} DAY),
                {days_ahead}
            ) AS forecasted_severity,
            AI.FORECAST(
                'critical_threats',
                threat_metrics,
                DATE_ADD(CURRENT_DATE(), INTERVAL {days_ahead} DAY),
                {days_ahead}
            ) AS forecasted_critical_threats
        FROM threat_metrics
        """
        
        return self._execute_ai_query(query, "threat_forecasting")
    
    def generate_vulnerability_analysis(self, vuln_info: str) -> Dict[str, Any]:
        """Generate vulnerability analysis using ML.GENERATE_TEXT (classic LLM)"""
        query = f"""
        SELECT
            ML.GENERATE_TEXT(
                'text-bison@001',
                'Analyze this supply chain vulnerability and provide: 1) Impact assessment, 2) Affected vendors, 3) Mitigation timeline, 4) Risk score (1-10)',
                '{vuln_info}'
            ) AS vulnerability_analysis,
            ML.GENERATE_TEXT(
                'text-bison@001',
                'Generate a CVSS-style score breakdown for this supply chain vulnerability',
                '{vuln_info}'
            ) AS cvss_breakdown
        """
        
        return self._execute_ai_query(query, "vulnerability_analysis")
    
    def generate_threat_intelligence(self, threat_data: str) -> Dict[str, Any]:
        """Generate comprehensive threat intelligence using multiple AI functions"""
        query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Extract key threat indicators and create a structured threat intelligence report for supply chain security teams.',
                '{threat_data}'
            ) AS threat_intel_report,
            AI.GENERATE_BOOL(
                'Is this threat specifically targeting supply chain infrastructure? Answer with true or false.',
                '{threat_data}'
            ) AS targets_supply_chain,
            AI.GENERATE_INT(
                'Rate the sophistication level of this threat actor from 1-10, where 10 is nation-state level.',
                '{threat_data}',
                1, 10
            ) AS actor_sophistication,
            AI.GENERATE_DOUBLE(
                'Calculate the estimated financial impact of this threat in millions of USD.',
                '{threat_data}',
                0.0, 1000.0
            ) AS estimated_financial_impact
        """
        
        return self._execute_ai_query(query, "threat_intelligence_generation")
    
    def generate_supply_chain_risk_assessment(self, vendor_data: str) -> Dict[str, Any]:
        """Generate supply chain risk assessment using AI functions"""
        query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Create a comprehensive supply chain risk assessment including: vendor criticality, dependency mapping, and risk mitigation strategies.',
                '{vendor_data}'
            ) AS risk_assessment,
            AI.GENERATE_TABLE(
                'Generate a risk matrix table with columns: Risk Category, Probability, Impact, Mitigation Priority',
                '{vendor_data}'
            ) AS risk_matrix,
            AI.GENERATE_TEXT(
                'List the top 5 supply chain dependencies that pose the highest risk.',
                '{vendor_data}'
            ) AS critical_dependencies
        """
        
        return self._execute_ai_query(query, "supply_chain_risk_assessment")
    
    def generate_incident_response_plan(self, incident_data: str) -> Dict[str, Any]:
        """Generate incident response plan using AI functions"""
        query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Create a detailed incident response plan for this supply chain security incident including: containment, eradication, recovery, and lessons learned.',
                '{incident_data}'
            ) AS incident_response_plan,
            AI.GENERATE_TEXT(
                'Generate a communication timeline for stakeholders including: immediate notification, status updates, and resolution announcement.',
                '{incident_data}'
            ) AS communication_timeline,
            AI.GENERATE_TEXT(
                'List the required resources and team members for effective incident response.',
                '{incident_data}'
            ) AS required_resources
        """
        
        return self._execute_ai_query(query, "incident_response_planning")
    
    def _execute_ai_query(self, query: str, query_type: str) -> Dict[str, Any]:
        """Execute AI query with cost monitoring and error handling"""
        start_time = time.time()
        
        try:
            console.print(f"🔍 Executing {query_type} query...")
            
            # Configure query job
            job_config = QueryJobConfig(
                use_query_cache=False,  # Disable cache for AI queries
                maximum_bytes_billed=config.max_query_bytes
            )
            
            # Execute query
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            # Process results
            data = []
            for row in results:
                row_dict = {}
                for key, value in row.items():
                    if hasattr(value, 'to_api_repr'):
                        row_dict[key] = value.to_api_repr()
                    else:
                        row_dict[key] = value
                data.append(row_dict)
            
            processing_time = time.time() - start_time
            
            # Estimate cost (AI queries have different pricing)
            estimated_cost = self._estimate_ai_query_cost(query_type, processing_time)
            
            # Track cost
            self.cost_monitor.track_query_cost(estimated_cost, query_type)
            
            console.print(f"✅ {query_type} completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "data": data,
                "query_type": query_type,
                "processing_time": processing_time,
                "estimated_cost_usd": estimated_cost,
                "rows_returned": len(data)
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            console.print(f"❌ {query_type} failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "query_type": query_type,
                "processing_time": processing_time
            }
    
    def _estimate_ai_query_cost(self, query_type: str, processing_time: float) -> float:
        """Estimate cost for AI queries based on type and processing time"""
        # Base costs for different AI function types
        base_costs = {
            "threat_summary_generation": 0.001,  # AI.GENERATE_TEXT
            "threat_forecasting": 0.002,         # AI.FORECAST
            "vulnerability_analysis": 0.001,     # ML.GENERATE_TEXT
            "threat_intelligence_generation": 0.003,  # Multiple AI functions
            "supply_chain_risk_assessment": 0.002,    # AI.GENERATE_TABLE
            "incident_response_planning": 0.002       # Multiple AI functions
        }
        
        base_cost = base_costs.get(query_type, 0.001)
        
        # Add time-based cost (longer queries cost more)
        time_multiplier = min(processing_time / 10.0, 2.0)  # Cap at 2x
        
        return base_cost * time_multiplier
    
    def run_comprehensive_ai_analysis(self, threat_report_id: str) -> Dict[str, Any]:
        """Run comprehensive AI analysis using all available functions"""
        console.print("🚀 Starting comprehensive AI analysis...")
        
        try:
            # Get threat data
            threat_data = self._get_threat_data(threat_report_id)
            if not threat_data:
                return {"success": False, "error": "Threat data not found"}
            
            # Run all AI analyses
            results = {
                "threat_summary": self.generate_threat_summary(threat_data["description"]),
                "vulnerability_analysis": self.generate_vulnerability_analysis(threat_data["description"]),
                "threat_intelligence": self.generate_threat_intelligence(threat_data["raw_report"]),
                "risk_assessment": self.generate_supply_chain_risk_assessment(threat_data["raw_report"]),
                "incident_response": self.generate_incident_response_plan(threat_data["raw_report"])
            }
            
            # Add forecasting
            results["threat_forecasting"] = self.forecast_threat_metrics()
            
            # Compile comprehensive report
            comprehensive_report = {
                "report_id": threat_report_id,
                "analysis_timestamp": time.time(),
                "ai_analysis_results": results,
                "overall_risk_score": self._calculate_overall_risk_score(results),
                "recommendations": self._generate_recommendations(results)
            }
            
            console.print("✅ Comprehensive AI analysis completed")
            return {"success": True, "data": comprehensive_report}
            
        except Exception as e:
            console.print(f"❌ Comprehensive analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_threat_data(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve threat data from BigQuery"""
        query = f"""
        SELECT * FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        WHERE report_id = '{report_id}'
        LIMIT 1
        """
        
        try:
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                return {
                    "description": row.description,
                    "raw_report": row.raw_report,
                    "severity": row.severity,
                    "threat_type": row.threat_type,
                    "vendor_name": row.vendor_name
                }
            return None
            
        except Exception as e:
            console.print(f"❌ Failed to retrieve threat data: {str(e)}")
            return None
    
    def _calculate_overall_risk_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall risk score from AI analysis results"""
        # Extract risk indicators from various analyses
        risk_indicators = []
        
        # Add severity from threat summary
        if results.get("threat_summary", {}).get("success"):
            risk_indicators.append(7.0)  # Default medium-high risk
        
        # Add vulnerability analysis risk
        if results.get("vulnerability_analysis", {}).get("success"):
            risk_indicators.append(6.5)  # Default medium-high risk
        
        # Calculate average risk score
        if risk_indicators:
            return sum(risk_indicators) / len(risk_indicators)
        return 5.0  # Default medium risk
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on AI analysis"""
        recommendations = [
            "Implement real-time threat monitoring for supply chain components",
            "Establish vendor security assessment protocols",
            "Create incident response playbooks for supply chain attacks",
            "Deploy AI-powered anomaly detection systems",
            "Conduct regular supply chain security audits"
        ]
        
        # Add specific recommendations based on analysis results
        if results.get("threat_intelligence", {}).get("success"):
            recommendations.append("Enhance threat intelligence sharing with industry partners")
        
        if results.get("risk_assessment", {}).get("success"):
            recommendations.append("Implement vendor risk scoring and monitoring")
        
        return recommendations

# Global instance
ai_sql_processor = AISQLProcessor()
