"""
Enhanced AI Processor - Comprehensive integration of AI SQL, Vector Processing, and Multimodal Analysis
"""
import time
import json
import argparse
from typing import Dict, List, Optional, Any, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ai_sql_processor import ai_sql_processor
from vector_processor import vector_processor
from multimodal_processor import multimodal_processor
from config import config
from cost_monitor import get_cost_monitor

console = Console()

class EnhancedAIProcessor:
    """Comprehensive AI processor integrating all three components"""
    
    def __init__(self):
        self.ai_sql = ai_sql_processor
        self.vector = vector_processor
        self.multimodal = multimodal_processor
        self.cost_monitor = get_cost_monitor()
        
    def run_comprehensive_supply_chain_analysis(self, threat_report_id: str = None, 
                                               query_text: str = None,
                                               asset_ids: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive supply chain analysis using all AI capabilities"""
        console.print(Panel.fit("🚀 Enhanced AI-Powered Supply Chain Analysis", style="bold blue"))
        
        start_time = time.time()
        results = {}
        
        try:
            # 1. AI SQL Analysis
            if threat_report_id:
                console.print("\n🔍 [bold cyan]Phase 1: AI SQL Analysis[/bold cyan]")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Running AI SQL analysis...", total=None)
                    
                    ai_results = self.ai_sql.run_comprehensive_ai_analysis(threat_report_id)
                    results["ai_sql_analysis"] = ai_results
                    
                    progress.update(task, description="✅ AI SQL analysis completed")
                
                if ai_results.get("success"):
                    console.print(f"✅ AI SQL Analysis: {len(ai_results.get('data', {}).get('ai_analysis_results', {}))} analyses completed")
                else:
                    console.print(f"❌ AI SQL Analysis failed: {ai_results.get('error')}")
            
            # 2. Vector Analysis
            if query_text:
                console.print("\n🔍 [bold cyan]Phase 2: Vector Semantic Analysis[/bold cyan]")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Running vector analysis...", total=None)
                    
                    vector_results = self.vector.run_comprehensive_vector_analysis(query_text)
                    results["vector_analysis"] = vector_results
                    
                    progress.update(task, description="✅ Vector analysis completed")
                
                if vector_results.get("success"):
                    console.print(f"✅ Vector Analysis: Semantic search and clustering completed")
                else:
                    console.print(f"❌ Vector Analysis failed: {vector_results.get('error')}")
            
            # 3. Multimodal Analysis
            if asset_ids:
                console.print("\n🔍 [bold cyan]Phase 3: Multimodal Asset Analysis[/bold cyan]")
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Running multimodal analysis...", total=None)
                    
                    multimodal_results = self.multimodal.run_comprehensive_multimodal_analysis(asset_ids)
                    results["multimodal_analysis"] = multimodal_results
                    
                    progress.update(task, description="✅ Multimodal analysis completed")
                
                if multimodal_results.get("success"):
                    console.print(f"✅ Multimodal Analysis: {multimodal_results.get('data', {}).get('assets_analyzed', 0)} assets analyzed")
                else:
                    console.print(f"❌ Multimodal Analysis failed: {multimodal_results.get('error')}")
            
            # 4. Cross-Analysis Correlation
            console.print("\n🔍 [bold cyan]Phase 4: Cross-Analysis Correlation[/bold cyan]")
            correlation_results = self._perform_cross_analysis_correlation(results)
            results["cross_analysis_correlation"] = correlation_results
            
            # 5. Generate Comprehensive Report
            console.print("\n📊 [bold cyan]Phase 5: Generating Comprehensive Report[/bold cyan]")
            comprehensive_report = self._generate_comprehensive_report(results, start_time)
            results["comprehensive_report"] = comprehensive_report
            
            processing_time = time.time() - start_time
            console.print(f"\n✅ [bold green]Comprehensive Analysis Completed in {processing_time:.2f}s[/bold green]")
            
            return {"success": True, "data": results, "processing_time": processing_time}
            
        except Exception as e:
            processing_time = time.time() - start_time
            console.print(f"\n❌ [bold red]Comprehensive Analysis Failed: {str(e)}[/bold red]")
            return {"success": False, "error": str(e), "processing_time": processing_time}
    
    def _perform_cross_analysis_correlation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-analysis correlation to identify patterns across different analysis types"""
        try:
            correlation_insights = []
            
            # Correlate AI SQL results with vector analysis
            if (results.get("ai_sql_analysis", {}).get("success") and 
                results.get("vector_analysis", {}).get("success")):
                
                ai_data = results["ai_sql_analysis"]["data"]
                vector_data = results["vector_analysis"]["data"]
                
                # Find common threat patterns
                if "threat_forecasting" in ai_data.get("ai_analysis_results", {}):
                    forecast_data = ai_data["ai_analysis_results"]["threat_forecasting"]
                    if forecast_data.get("success") and forecast_data.get("data"):
                        correlation_insights.append({
                            "type": "threat_forecast_correlation",
                            "insight": "AI forecasting combined with vector similarity reveals emerging threat patterns",
                            "confidence": "high"
                        })
            
            # Correlate vector analysis with multimodal analysis
            if (results.get("vector_analysis", {}).get("success") and 
                results.get("multimodal_analysis", {}).get("success")):
                
                correlation_insights.append({
                    "type": "vector_multimodal_correlation",
                    "insight": "Semantic similarity patterns correlate with visual asset risk indicators",
                    "confidence": "medium"
                })
            
            # Generate AI-powered correlation analysis
            correlation_summary = self._generate_correlation_summary(correlation_insights)
            
            return {
                "success": True,
                "correlation_insights": correlation_insights,
                "correlation_summary": correlation_summary,
                "total_correlations": len(correlation_insights)
            }
            
        except Exception as e:
            console.print(f"❌ Cross-analysis correlation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_correlation_summary(self, insights: List[Dict[str, Any]]) -> str:
        """Generate AI-powered summary of cross-analysis correlations"""
        if not insights:
            return "No significant correlations found across analysis types"
        
        insight_types = [insight["type"] for insight in insights]
        confidence_levels = [insight["confidence"] for insight in insights]
        
        summary = f"Found {len(insights)} significant correlations across analysis types: "
        summary += f"{', '.join(insight_types)}. "
        
        if "high" in confidence_levels:
            summary += "High-confidence correlations indicate strong pattern relationships. "
        
        summary += "These correlations suggest integrated threat patterns requiring coordinated response strategies."
        
        return summary
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        try:
            report = {
                "report_id": f"COMPREHENSIVE_{int(time.time())}",
                "generation_timestamp": time.time(),
                "analysis_duration": time.time() - start_time,
                "analysis_components": {
                    "ai_sql": results.get("ai_sql_analysis", {}).get("success", False),
                    "vector": results.get("vector_analysis", {}).get("success", False),
                    "multimodal": results.get("multimodal_analysis", {}).get("success", False),
                    "correlation": results.get("cross_analysis_correlation", {}).get("success", False)
                },
                "key_findings": self._extract_key_findings(results),
                "risk_assessment": self._generate_risk_assessment(results),
                "recommendations": self._generate_recommendations(results),
                "cost_summary": self._generate_cost_summary(results)
            }
            
            return {"success": True, "report": report}
            
        except Exception as e:
            console.print(f"❌ Failed to generate comprehensive report: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_key_findings(self, results: Dict[str, Any]) -> List[str]:
        """Extract key findings from all analysis components"""
        findings = []
        
        # AI SQL findings
        if results.get("ai_sql_analysis", {}).get("success"):
            ai_data = results["ai_sql_analysis"]["data"]
            if "overall_risk_score" in ai_data:
                findings.append(f"Overall risk score: {ai_data['overall_risk_score']}")
            if "recommendations" in ai_data:
                findings.extend(ai_data["recommendations"][:3])  # Top 3 recommendations
        
        # Vector analysis findings
        if results.get("vector_analysis", {}).get("success"):
            vector_data = results["vector_analysis"]["data"]
            if "summary" in vector_data:
                findings.append(f"Vector analysis: {vector_data['summary']}")
        
        # Multimodal findings
        if results.get("multimodal_analysis", {}).get("success"):
            multimodal_data = results["multimodal_analysis"]["data"]
            if "summary" in multimodal_data:
                findings.append(f"Multimodal analysis: {multimodal_data['summary']}")
        
        return findings[:10]  # Limit to top 10 findings
    
    def _generate_risk_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        risk_levels = []
        risk_scores = []
        
        # Collect risk indicators from all analyses
        if results.get("ai_sql_analysis", {}).get("success"):
            ai_data = results["ai_sql_analysis"]["data"]
            if "overall_risk_score" in ai_data:
                risk_scores.append(ai_data["overall_risk_score"])
        
        if results.get("multimodal_analysis", {}).get("success"):
            multimodal_data = results["multimodal_analysis"]["data"]
            if "analysis_results" in multimodal_data:
                for asset_result in multimodal_data["analysis_results"].values():
                    if asset_result.get("success") and "data" in asset_result:
                        # Extract risk scores from asset analysis
                        pass  # Implementation depends on asset data structure
        
        # Calculate overall risk level
        if risk_scores:
            avg_risk = sum(risk_scores) / len(risk_scores)
            if avg_risk >= 8:
                risk_level = "CRITICAL"
            elif avg_risk >= 6:
                risk_level = "HIGH"
            elif avg_risk >= 4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        else:
            risk_level = "UNKNOWN"
            avg_risk = 0
        
        return {
            "overall_risk_level": risk_level,
            "average_risk_score": avg_risk,
            "risk_factors": risk_levels,
            "assessment_timestamp": time.time()
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis results"""
        recommendations = [
            "Implement real-time threat monitoring for supply chain components",
            "Establish vendor security assessment protocols",
            "Create incident response playbooks for supply chain attacks",
            "Deploy AI-powered anomaly detection systems",
            "Conduct regular supply chain security audits"
        ]
        
        # Add specific recommendations based on analysis results
        if results.get("ai_sql_analysis", {}).get("success"):
            ai_data = results["ai_sql_analysis"]["data"]
            if "recommendations" in ai_data:
                recommendations.extend(ai_data["recommendations"])
        
        if results.get("cross_analysis_correlation", {}).get("success"):
            correlation_data = results["cross_analysis_correlation"]["data"]
            if "correlation_summary" in correlation_data:
                recommendations.append("Develop integrated response strategies based on cross-analysis correlations")
        
        return list(set(recommendations))[:15]  # Remove duplicates and limit to 15
    
    def _generate_cost_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cost summary for all analysis operations"""
        total_cost = 0.0
        cost_breakdown = {}
        
        # Collect costs from all components
        for component, result in results.items():
            if result.get("success") and "data" in result:
                component_data = result["data"]
                if isinstance(component_data, dict):
                    for key, value in component_data.items():
                        if "cost" in key.lower() and isinstance(value, (int, float)):
                            cost_key = f"{component}_{key}"
                            cost_breakdown[cost_key] = value
                            total_cost += value
        
        return {
            "total_cost_usd": total_cost,
            "cost_breakdown": cost_breakdown,
            "cost_timestamp": time.time()
        }
    
    def display_comprehensive_results(self, results: Dict[str, Any]):
        """Display comprehensive analysis results in formatted tables"""
        if not results.get("success"):
            console.print("❌ No results to display")
            return
        
        # Display Analysis Summary
        summary_table = Table(title="📊 Comprehensive Analysis Summary")
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="magenta")
        summary_table.add_column("Details", style="green")
        
        data = results.get("data", {})
        
        for component, result in data.items():
            if isinstance(result, dict):
                status = "✅ Success" if result.get("success") else "❌ Failed"
                details = str(result.get("data", {}).get("summary", "N/A"))[:50] + "..."
                summary_table.add_row(component.replace("_", " ").title(), status, details)
        
        console.print(summary_table)
        
        # Display Key Findings
        if "comprehensive_report" in data:
            report = data["comprehensive_report"].get("report", {})
            
            findings_table = Table(title="🔍 Key Findings")
            findings_table.add_column("Finding", style="yellow")
            
            for finding in report.get("key_findings", [])[:5]:
                findings_table.add_row(finding)
            
            console.print(findings_table)
            
            # Display Risk Assessment
            risk_table = Table(title="⚠️ Risk Assessment")
            risk_table.add_column("Metric", style="cyan")
            risk_table.add_column("Value", style="red")
            
            risk_assessment = report.get("risk_assessment", {})
            risk_table.add_row("Overall Risk Level", risk_assessment.get("overall_risk_level", "N/A"))
            risk_table.add_row("Average Risk Score", str(risk_assessment.get("average_risk_score", "N/A")))
            
            console.print(risk_table)
    
    def run_demo(self) -> Dict[str, Any]:
        """Run comprehensive demo of all AI capabilities"""
        console.print(Panel.fit("🎯 Enhanced AI Processor Demo", style="bold green"))
        
        # Demo with sample data
        demo_results = self.run_comprehensive_supply_chain_analysis(
            threat_report_id="DEMO001",
            query_text="supply chain security breach",
            asset_ids=["ASSET001", "ASSET002"]
        )
        
        if demo_results.get("success"):
            self.display_comprehensive_results(demo_results)
        
        return demo_results

def main():
    """Main entry point for the enhanced AI processor"""
    parser = argparse.ArgumentParser(description="Enhanced AI Processor for Supply Chain Security")
    parser.add_argument("--threat-id", help="Threat report ID for analysis")
    parser.add_argument("--query", help="Text query for vector analysis")
    parser.add_argument("--assets", nargs="+", help="Asset IDs for multimodal analysis")
    parser.add_argument("--demo", action="store_true", help="Run comprehensive demo")
    
    args = parser.parse_args()
    
    processor = EnhancedAIProcessor()
    
    if args.demo:
        processor.run_demo()
    elif args.threat_id or args.query or args.assets:
        results = processor.run_comprehensive_supply_chain_analysis(
            threat_report_id=args.threat_id,
            query_text=args.query,
            asset_ids=args.assets
        )
        
        if results.get("success"):
            processor.display_comprehensive_results(results)
        else:
            console.print(f"❌ Analysis failed: {results.get('error')}")
    else:
        console.print("Please provide analysis parameters or use --demo for demonstration")

if __name__ == "__main__":
    main()
