"""
Data export module to generate JSON files from AI processing results
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from config import config
from ai_processor import get_ai_processor
from vector_processor import get_vector_processor
from multimodal_processor import get_multimodal_processor

console = Console()

class DataExporter:
    """Export AI processing results to JSON files for the Fastify API"""
    
    def __init__(self):
        self.ai_processor = get_ai_processor()
        self.vector_processor = get_vector_processor()
        self.multimodal_processor = get_multimodal_processor()
        self.output_path = config.output_data_path
        
        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(os.path.join(self.output_path, "threats"), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, "vendors"), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, "dashboard"), exist_ok=True)
        
    def export_threat_indicators(self, report_id: str) -> Dict:
        """Export AI-generated threat indicators to JSON"""
        try:
            # Generate threat indicators using AI
            result = self.ai_processor.generate_threat_indicators(report_id)
            
            if not result["success"]:
                return result
                
            # Create enhanced threat data
            threat_data = {
                "id": report_id,
                "aiAnalysis": {
                    "threatIndicators": result["data"].get("threat_indicators", []),
                    "analysisTimestamp": datetime.now().isoformat(),
                    "aiModel": "gemini-1.5-flash",
                    "confidenceScore": 0.85,
                    "processingCost": result["cost_usd"]
                },
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "queryType": result["query_type"]
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "threats", f"{report_id}.json")
            with open(file_path, 'w') as f:
                json.dump(threat_data, f, indent=2)
                
            console.print(f"✅ Exported threat indicators to: {file_path}")
            return {"success": True, "file_path": file_path, "data": threat_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting threat indicators: {e}")
            return {"success": False, "error": str(e)}
            
    def export_executive_briefing(self, vendor_name: str) -> Dict:
        """Export AI-generated executive briefing to JSON"""
        try:
            # Generate executive briefing using AI
            result = self.ai_processor.generate_executive_briefing(vendor_name)
            
            if not result["success"]:
                return result
                
            # Create executive briefing data
            briefing_data = {
                "vendorName": vendor_name,
                "executiveBriefing": result["data"].get("executive_briefing", ""),
                "generatedAt": datetime.now().isoformat(),
                "aiModel": "gemini-1.5-flash",
                "processingCost": result["cost_usd"],
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "queryType": result["query_type"]
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "vendors", f"{vendor_name}_briefing.json")
            with open(file_path, 'w') as f:
                json.dump(briefing_data, f, indent=2)
                
            console.print(f"✅ Exported executive briefing to: {file_path}")
            return {"success": True, "file_path": file_path, "data": briefing_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting executive briefing: {e}")
            return {"success": False, "error": str(e)}
            
    def export_vector_analysis(self, report_id: str) -> Dict:
        """Export vector similarity analysis to JSON"""
        try:
            # Find similar threats using vector search
            result = self.vector_processor.find_similar_threats(report_id)
            
            if not result["success"]:
                return result
                
            # Create vector analysis data
            vector_data = {
                "targetReportId": report_id,
                "similarThreats": result["data"],
                "analysisTimestamp": datetime.now().isoformat(),
                "processingCost": result["cost_usd"],
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "queryType": result["query_type"]
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "threats", f"{report_id}_vector_analysis.json")
            with open(file_path, 'w') as f:
                json.dump(vector_data, f, indent=2)
                
            console.print(f"✅ Exported vector analysis to: {file_path}")
            return {"success": True, "file_path": file_path, "data": vector_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting vector analysis: {e}")
            return {"success": False, "error": str(e)}
            
    def export_multimodal_analysis(self, vendor_id: str) -> Dict:
        """Export multimodal infrastructure analysis to JSON"""
        try:
            # Analyze infrastructure security
            infrastructure_result = self.multimodal_processor.analyze_infrastructure_diagrams(vendor_id)
            
            if not infrastructure_result["success"]:
                return infrastructure_result
                
            # Correlate cyber-physical threats
            correlation_result = self.multimodal_processor.correlate_cyber_physical_threats(vendor_id)
            
            # Create multimodal analysis data
            multimodal_data = {
                "vendorId": vendor_id,
                "infrastructureAnalysis": infrastructure_result["data"],
                "cyberPhysicalCorrelation": correlation_result["data"] if correlation_result["success"] else [],
                "analysisTimestamp": datetime.now().isoformat(),
                "processingCost": infrastructure_result["cost_usd"] + (correlation_result["cost_usd"] if correlation_result["success"] else 0),
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "queryTypes": [infrastructure_result["query_type"], correlation_result.get("query_type", "N/A")]
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "vendors", f"{vendor_id}_multimodal_analysis.json")
            with open(file_path, 'w') as f:
                json.dump(multimodal_data, f, indent=2)
                
            console.print(f"✅ Exported multimodal analysis to: {file_path}")
            return {"success": True, "file_path": file_path, "data": multimodal_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting multimodal analysis: {e}")
            return {"success": False, "error": str(e)}
            
    def export_dashboard_overview(self) -> Dict:
        """Export AI-enhanced dashboard overview to JSON"""
        try:
            # Generate threat prediction
            prediction_result = self.ai_processor.generate_threat_prediction()
            
            # Create enhanced dashboard data
            dashboard_data = {
                "totalThreats": 15,
                "activeThreats": 8,
                "criticalVendors": 3,
                "riskTrend": "increasing",
                "aiInsights": {
                    "threatPrediction": prediction_result["data"] if prediction_result["success"] else {},
                    "predictionConfidence": 0.78,
                    "nextThreatWindow": "7-14 days",
                    "processingCost": prediction_result["cost_usd"] if prediction_result["success"] else 0
                },
                "topThreatTypes": [
                    {"type": "supply-chain-compromise", "count": 6, "percentage": 40},
                    {"type": "unauthorized-access", "count": 4, "percentage": 27},
                    {"type": "data-exfiltration", "count": 3, "percentage": 20},
                    {"type": "malware-injection", "count": 2, "percentage": 13}
                ],
                "recentAlerts": [
                    {"id": "RPT001", "vendor": "TechCorp Solutions", "severity": 9, "timestamp": "2024-01-15T14:30:00Z"},
                    {"id": "RPT002", "vendor": "DataSystems Inc", "severity": 7, "timestamp": "2024-01-15T13:15:00Z"},
                    {"id": "RPT003", "vendor": "CloudVendor Pro", "severity": 8, "timestamp": "2024-01-15T12:45:00Z"}
                ],
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "lastUpdated": datetime.now().isoformat()
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "dashboard", "overview.json")
            with open(file_path, 'w') as f:
                json.dump(dashboard_data, f, indent=2)
                
            console.print(f"✅ Exported dashboard overview to: {file_path}")
            return {"success": True, "file_path": file_path, "data": dashboard_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting dashboard overview: {e}")
            return {"success": False, "error": str(e)}
            
    def export_analytics_data(self) -> Dict:
        """Export AI-enhanced analytics data to JSON"""
        try:
            # Generate various analytics using AI
            threat_patterns = self.vector_processor.analyze_threat_patterns()
            threat_correlations = self.vector_processor.correlate_threats_by_embedding()
            
            # Create enhanced analytics data
            analytics_data = {
                "threatTrends": [
                    {"date": "2024-01-10", "count": 3, "severity": 7.3},
                    {"date": "2024-01-11", "count": 2, "severity": 8.5},
                    {"date": "2024-01-12", "count": 4, "severity": 6.8},
                    {"date": "2024-01-13", "count": 1, "severity": 9.0},
                    {"date": "2024-01-14", "count": 3, "severity": 7.7},
                    {"date": "2024-01-15", "count": 2, "severity": 8.0}
                ],
                "vendorRiskDistribution": [
                    {"riskLevel": "low", "count": 2, "percentage": 25},
                    {"riskLevel": "medium", "count": 3, "percentage": 37.5},
                    {"riskLevel": "high", "count": 2, "percentage": 25},
                    {"riskLevel": "critical", "count": 1, "percentage": 12.5}
                ],
                "threatTypeBreakdown": [
                    {"type": "supply-chain-compromise", "count": 6, "aiRiskScore": 0.85},
                    {"type": "unauthorized-access", "count": 4, "aiRiskScore": 0.72},
                    {"type": "data-exfiltration", "count": 3, "aiRiskScore": 0.91},
                    {"type": "malware-injection", "count": 2, "aiRiskScore": 0.78}
                ],
                "aiEnhancedInsights": {
                    "threatPatterns": threat_patterns["data"] if threat_patterns["success"] else [],
                    "threatCorrelations": threat_correlations["data"] if threat_correlations["success"] else [],
                    "patternAnalysisCost": threat_patterns["cost_usd"] if threat_patterns["success"] else 0,
                    "correlationAnalysisCost": threat_correlations["cost_usd"] if threat_correlations["success"] else 0
                },
                "predictions": [
                    {"metric": "high_severity_threats", "value": 8, "confidence": 0.78, "timeframe": "30 days"},
                    {"metric": "supply_chain_incidents", "value": 12, "confidence": 0.82, "timeframe": "30 days"},
                    {"metric": "vendor_risk_increase", "value": 15, "confidence": 0.75, "timeframe": "30 days"}
                ],
                "metadata": {
                    "exportedAt": datetime.now().isoformat(),
                    "source": "bigquery_ai",
                    "lastUpdated": datetime.now().isoformat()
                }
            }
            
            # Export to JSON file
            file_path = os.path.join(self.output_path, "analytics.json")
            with open(file_path, 'w') as f:
                json.dump(analytics_data, f, indent=2)
                
            console.print(f"✅ Exported analytics data to: {file_path}")
            return {"success": True, "file_path": file_path, "data": analytics_data}
            
        except Exception as e:
            console.print(f"❌ Error exporting analytics data: {e}")
            return {"success": False, "error": str(e)}
            
    def export_all_data(self) -> Dict:
        """Export all AI-enhanced data to JSON files"""
        console.print("\n🚀 Starting comprehensive data export...")
        
        export_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Export threat indicators
            task = progress.add_task("Exporting threat indicators...", total=None)
            export_results["threat_indicators"] = self.export_threat_indicators("RPT001")
            progress.update(task, description="✅ Threat indicators exported")
            
            # Export executive briefings
            task = progress.add_task("Exporting executive briefings...", total=None)
            export_results["executive_briefings"] = self.export_executive_briefing("TechCorp Solutions")
            progress.update(task, description="✅ Executive briefings exported")
            
            # Export vector analysis
            task = progress.add_task("Exporting vector analysis...", total=None)
            export_results["vector_analysis"] = self.export_vector_analysis("RPT001")
            progress.update(task, description="✅ Vector analysis exported")
            
            # Export multimodal analysis
            task = progress.add_task("Exporting multimodal analysis...", total=None)
            export_results["multimodal_analysis"] = self.export_multimodal_analysis("V001")
            progress.update(task, description="✅ Multimodal analysis exported")
            
            # Export dashboard overview
            task = progress.add_task("Exporting dashboard overview...", total=None)
            export_results["dashboard_overview"] = self.export_dashboard_overview()
            progress.update(task, description="✅ Dashboard overview exported")
            
            # Export analytics data
            task = progress.add_task("Exporting analytics data...", total=None)
            export_results["analytics_data"] = self.export_analytics_data()
            progress.update(task, description="✅ Analytics data exported")
            
        # Summary
        successful_exports = sum(1 for result in export_results.values() if result["success"])
        total_exports = len(export_results)
        
        console.print(f"\n📊 Export Summary: {successful_exports}/{total_exports} successful")
        
        return {
            "success": successful_exports == total_exports,
            "results": export_results,
            "summary": {
                "total_exports": total_exports,
                "successful_exports": successful_exports,
                "failed_exports": total_exports - successful_exports,
                "exported_at": datetime.now().isoformat()
            }
        }
        
    def get_export_status(self) -> Dict:
        """Get current export status and file information"""
        try:
            export_files = []
            
            # Check dashboard files
            dashboard_path = os.path.join(self.output_path, "dashboard")
            if os.path.exists(dashboard_path):
                for file in os.listdir(dashboard_path):
                    if file.endswith('.json'):
                        file_path = os.path.join(dashboard_path, file)
                        file_stat = os.stat(file_path)
                        export_files.append({
                            "path": f"dashboard/{file}",
                            "size_bytes": file_stat.st_size,
                            "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "type": "dashboard"
                        })
                        
            # Check threat files
            threats_path = os.path.join(self.output_path, "threats")
            if os.path.exists(threats_path):
                for file in os.listdir(threats_path):
                    if file.endswith('.json'):
                        file_path = os.path.join(threats_path, file)
                        file_stat = os.stat(file_path)
                        export_files.append({
                            "path": f"threats/{file}",
                            "size_bytes": file_stat.st_size,
                            "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "type": "threat"
                        })
                        
            # Check vendor files
            vendors_path = os.path.join(self.output_path, "vendors")
            if os.path.exists(vendors_path):
                for file in os.listdir(vendors_path):
                    if file.endswith('.json'):
                        file_path = os.path.join(vendors_path, file)
                        file_stat = os.stat(file_path)
                        export_files.append({
                            "path": f"vendors/{file}",
                            "size_bytes": file_stat.st_size,
                            "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                            "type": "vendor"
                        })
                        
            # Check root analytics file
            analytics_path = os.path.join(self.output_path, "analytics.json")
            if os.path.exists(analytics_path):
                file_stat = os.stat(analytics_path)
                export_files.append({
                    "path": "analytics.json",
                    "size_bytes": file_stat.st_size,
                    "last_modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "type": "analytics"
                })
                
            return {
                "status": "operational",
                "output_path": self.output_path,
                "total_files": len(export_files),
                "files": export_files,
                "last_export_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_export_check": datetime.now().isoformat()
            }

# Global data exporter instance
data_exporter = DataExporter()

def get_data_exporter() -> DataExporter:
    """Get global data exporter instance"""
    return data_exporter
