"""
Multimodal Processor - Implements ObjectRef and AI analysis for unstructured supply chain data
"""
import time
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from google.cloud import bigquery, storage
from google.cloud.bigquery import QueryJobConfig
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import bigframes as bf
from bigframes.ml.llm import GeminiTextGenerator

from config import config
from cost_monitor import get_cost_monitor

console = Console()

class MultimodalProcessor:
    """Comprehensive multimodal processor for unstructured supply chain data"""
    
    def __init__(self):
        self.client = bigquery.Client(project=config.gcp_project_id)
        self.storage_client = storage.Client(project=config.gcp_project_id)
        self.cost_monitor = get_cost_monitor()
        self.session = bf.get_global_session()
        
    def create_supply_chain_assets_table(self) -> Dict[str, Any]:
        """Create supply chain assets table with ObjectRef support"""
        table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets"
        
        schema = [
            bigquery.SchemaField("asset_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("asset_type", "STRING", mode="REQUIRED"),  # image, document, video, etc.
            bigquery.SchemaField("vendor_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("asset_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("asset_description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("evidence_obj", "OBJECT", mode="NULLABLE"),  # ObjectRef for the actual file
            bigquery.SchemaField("metadata", "STRING", mode="NULLABLE"),  # JSON string for additional metadata
            bigquery.SchemaField("risk_score", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("upload_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("last_analyzed", "TIMESTAMP", mode="NULLABLE")
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            self.client.get_table(table)
            console.print(f"✅ Supply chain assets table already exists")
            return {"success": True, "message": "Table already exists"}
        except Exception:
            self.client.create_table(table)
            console.print(f"✅ Created supply chain assets table")
            return {"success": True, "message": "Table created successfully"}
    
    def upload_asset_to_gcs(self, file_path: str, asset_id: str, asset_type: str) -> Dict[str, Any]:
        """Upload asset file to Google Cloud Storage and return ObjectRef"""
        try:
            bucket_name = f"{config.gcp_project_id}-supply-chain-assets"
            
            # Create bucket if it doesn't exist
            try:
                bucket = self.storage_client.get_bucket(bucket_name)
            except Exception:
                bucket = self.storage_client.create_bucket(bucket_name, location=config.gcp_location)
                console.print(f"✅ Created bucket: {bucket_name}")
            
            # Upload file
            blob_name = f"{asset_type}/{asset_id}/{os.path.basename(file_path)}"
            blob = bucket.blob(blob_name)
            
            blob.upload_from_filename(file_path)
            console.print(f"✅ Uploaded {file_path} to gs://{bucket_name}/{blob_name}")
            
            # Return ObjectRef information
            object_ref = {
                "bucket": bucket_name,
                "name": blob_name,
                "generation": blob.generation,
                "size": blob.size,
                "content_type": blob.content_type,
                "md5_hash": blob.md5_hash
            }
            
            return {
                "success": True,
                "object_ref": object_ref,
                "gcs_uri": f"gs://{bucket_name}/{blob_name}"
            }
            
        except Exception as e:
            console.print(f"❌ Failed to upload asset: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def insert_asset_record(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert asset record into BigQuery with ObjectRef"""
        try:
            table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets"
            
            # Prepare the insert query
            insert_query = f"""
            INSERT INTO `{table_id}` (
                asset_id, asset_type, vendor_id, asset_name, asset_description,
                evidence_obj, metadata, risk_score, upload_timestamp
            ) VALUES (
                @asset_id, @asset_type, @vendor_id, @asset_name, @asset_description,
                @evidence_obj, @metadata, @risk_score, @upload_timestamp
            )
            """
            
            # Execute insert
            job_config = QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("asset_id", "STRING", asset_data["asset_id"]),
                    bigquery.ScalarQueryParameter("asset_type", "STRING", asset_data["asset_type"]),
                    bigquery.ScalarQueryParameter("vendor_id", "STRING", asset_data["vendor_id"]),
                    bigquery.ScalarQueryParameter("asset_name", "STRING", asset_data["asset_name"]),
                    bigquery.ScalarQueryParameter("asset_description", "STRING", asset_data["asset_description"]),
                    bigquery.ScalarQueryParameter("evidence_obj", "STRING", json.dumps(asset_data["evidence_obj"])),
                    bigquery.ScalarQueryParameter("metadata", "STRING", asset_data.get("metadata", "{}")),
                    bigquery.ScalarQueryParameter("risk_score", "FLOAT64", asset_data["risk_score"]),
                    bigquery.ScalarQueryParameter("upload_timestamp", "TIMESTAMP", asset_data["upload_timestamp"])
                ]
            )
            
            query_job = self.client.query(insert_query, job_config=job_config)
            query_job.result()
            
            console.print(f"✅ Asset record inserted: {asset_data['asset_id']}")
            return {"success": True, "asset_id": asset_data["asset_id"]}
            
        except Exception as e:
            console.print(f"❌ Failed to insert asset record: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_asset_with_ai(self, asset_id: str) -> Dict[str, Any]:
        """Analyze asset using AI + ObjectRef for multimodal content"""
        try:
            # Get asset information
            asset_query = f"""
            SELECT 
                asset_id,
                asset_type,
                vendor_id,
                asset_name,
                asset_description,
                evidence_obj,
                risk_score
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
            WHERE asset_id = '{asset_id}'
            LIMIT 1
            """
            
            query_job = self.client.query(asset_query)
            results = list(query_job.result())
            
            if not results:
                return {"success": False, "error": "Asset not found"}
            
            asset = results[0]
            
            # Perform AI analysis based on asset type
            if asset.asset_type == "image":
                analysis_result = self._analyze_image_asset(asset)
            elif asset.asset_type == "document":
                analysis_result = self._analyze_document_asset(asset)
            elif asset.asset_type == "video":
                analysis_result = self._analyze_video_asset(asset)
            else:
                analysis_result = self._analyze_generic_asset(asset)
            
            # Update last_analyzed timestamp
            self._update_analysis_timestamp(asset_id)
            
            return analysis_result
            
        except Exception as e:
            console.print(f"❌ Failed to analyze asset: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _analyze_image_asset(self, asset: Any) -> Dict[str, Any]:
        """Analyze image asset using AI.GENERATE_TEXT with ObjectRef"""
        analysis_query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Analyze this supply chain infrastructure image and identify: 1) Security vulnerabilities, 2) Risk factors, 3) Compliance issues, 4) Recommended actions. Provide detailed analysis suitable for security teams.',
                evidence_obj
            ) AS security_analysis,
            AI.GENERATE_TEXT(
                'Generate a detailed caption describing the contents of this image for supply chain security documentation.',
                evidence_obj
            ) AS image_caption,
            AI.GENERATE_TEXT(
                'Based on this image, what are the top 3 supply chain security concerns and their potential impact?',
                evidence_obj
            ) AS security_concerns
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
        WHERE asset_id = '{asset.asset_id}'
        """
        
        return self._execute_multimodal_query(analysis_query, "image_analysis")
    
    def _analyze_document_asset(self, asset: Any) -> Dict[str, Any]:
        """Analyze document asset using AI functions"""
        analysis_query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Extract key security information from this supply chain document including: 1) Vendor details, 2) Security requirements, 3) Compliance status, 4) Risk indicators, 5) Action items.',
                evidence_obj
            ) AS document_analysis,
            AI.GENERATE_TEXT(
                'Summarize the main security findings and recommendations from this document in 3-4 bullet points.',
                evidence_obj
            ) AS security_summary,
            AI.GENERATE_BOOL(
                'Does this document indicate any immediate security risks that require urgent attention? Answer true or false.',
                evidence_obj
            ) AS urgent_attention_required
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
        WHERE asset_id = '{asset.asset_id}'
        """
        
        return self._execute_multimodal_query(analysis_query, "document_analysis")
    
    def _analyze_video_asset(self, asset: Any) -> Dict[str, Any]:
        """Analyze video asset using AI functions"""
        analysis_query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Analyze this supply chain security video and identify: 1) Key security events, 2) Threat indicators, 3) Vulnerable areas, 4) Security recommendations. Provide timestamp-based analysis.',
                evidence_obj
            ) AS video_analysis,
            AI.GENERATE_TEXT(
                'Create a security incident timeline from this video with key events and their significance.',
                evidence_obj
            ) AS incident_timeline,
            AI.GENERATE_INT(
                'Rate the overall security risk level shown in this video from 1-10, where 10 is critical.',
                evidence_obj,
                1, 10
            ) AS video_risk_score
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
        WHERE asset_id = '{asset.asset_id}'
        """
        
        return self._execute_multimodal_query(analysis_query, "video_analysis")
    
    def _analyze_generic_asset(self, asset: Any) -> Dict[str, Any]:
        """Analyze generic asset using AI functions"""
        analysis_query = f"""
        SELECT
            AI.GENERATE_TEXT(
                'Analyze this supply chain asset and provide: 1) Asset classification, 2) Security assessment, 3) Risk evaluation, 4) Compliance status, 5) Recommendations.',
                evidence_obj
            ) AS generic_analysis,
            AI.GENERATE_TEXT(
                'What type of supply chain security threat could this asset represent and how should it be mitigated?',
                evidence_obj
            ) AS threat_assessment
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
        WHERE asset_id = '{asset.asset_id}'
        """
        
        return self._execute_multimodal_query(analysis_query, "generic_analysis")
    
    def perform_bigframes_multimodal_analysis(self, text_data: List[str], image_data: List[str] = None) -> Dict[str, Any]:
        """Perform multimodal analysis using BigFrames GeminiTextGenerator"""
        try:
            console.print("🔍 Performing BigFrames multimodal analysis...")
            start_time = time.time()
            
            # Create DataFrame with text data
            df = self.session.create_dataframe(text_data, columns=["text"])
            
            # Add image data if provided
            if image_data:
                df = df.assign(image=image_data)
            
            # Generate multimodal analysis using Gemini
            gemini = GeminiTextGenerator()
            
            if image_data:
                # Multimodal analysis with images
                analysis_prompt = "Analyze this supply chain security content and provide: 1) Key findings, 2) Risk assessment, 3) Recommendations"
                analysis_results = gemini.generate(df[["text", "image"]], prompt=analysis_prompt)
            else:
                # Text-only analysis
                analysis_prompt = "Analyze this supply chain security text and provide: 1) Key findings, 2) Risk assessment, 3) Recommendations"
                analysis_results = gemini.generate(df["text"], prompt=analysis_prompt)
            
            # Add analysis results to DataFrame
            df_with_analysis = df.assign(ai_analysis=analysis_results)
            
            processing_time = time.time() - start_time
            
            console.print(f"✅ BigFrames multimodal analysis completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "data": {
                    "texts_analyzed": len(text_data),
                    "images_analyzed": len(image_data) if image_data else 0,
                    "analysis_results": analysis_results.tolist() if hasattr(analysis_results, 'tolist') else str(analysis_results),
                    "processing_time": processing_time
                }
            }
            
        except Exception as e:
            console.print(f"❌ BigFrames multimodal analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_object_table_for_assets(self) -> Dict[str, Any]:
        """Create Object Table to store and reference files"""
        try:
            # Create object table using BigQuery Object Tables
            table_id = f"{config.gcp_project_id}.{config.gcp_dataset_id}.asset_objects"
            
            # Note: Object Tables are created differently in BigQuery
            # This is a conceptual implementation
            create_query = f"""
            CREATE TABLE `{table_id}` (
                asset_id STRING,
                evidence_obj ObjectRef,
                comment STRING,
                created_at TIMESTAMP
            )
            """
            
            # For now, we'll create a regular table and simulate ObjectRef functionality
            schema = [
                bigquery.SchemaField("asset_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("evidence_obj", "STRING", mode="NULLABLE"),  # Simulated ObjectRef
                bigquery.SchemaField("comment", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
            ]
            
            table = bigquery.Table(table_id, schema=schema)
            
            try:
                self.client.get_table(table)
                console.print(f"✅ Asset objects table already exists")
                return {"success": True, "message": "Table already exists"}
            except Exception:
                self.client.create_table(table)
                console.print(f"✅ Created asset objects table")
                return {"success": True, "message": "Table created successfully"}
                
        except Exception as e:
            console.print(f"❌ Failed to create object table: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_multimodal_query(self, query: str, query_type: str) -> Dict[str, Any]:
        """Execute multimodal AI query with cost monitoring and error handling"""
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
            
            # Estimate cost for multimodal operations
            estimated_cost = self._estimate_multimodal_query_cost(query_type, processing_time)
            
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
    
    def _estimate_multimodal_query_cost(self, query_type: str, processing_time: float) -> float:
        """Estimate cost for multimodal queries based on type and processing time"""
        # Base costs for different multimodal operation types
        base_costs = {
            "image_analysis": 0.002,      # AI.GENERATE_TEXT with ObjectRef
            "document_analysis": 0.003,    # Multiple AI functions with ObjectRef
            "video_analysis": 0.004,       # Complex multimodal analysis
            "generic_analysis": 0.002,     # Standard AI analysis
            "multimodal_processing": 0.005 # BigFrames + Gemini operations
        }
        
        base_cost = base_costs.get(query_type, 0.002)
        
        # Add time-based cost
        time_multiplier = min(processing_time / 8.0, 2.5)  # Cap at 2.5x
        
        return base_cost * time_multiplier
    
    def _update_analysis_timestamp(self, asset_id: str) -> bool:
        """Update the last_analyzed timestamp for an asset"""
        try:
            update_query = f"""
            UPDATE `{config.gcp_project_id}.{config.gcp_dataset_id}.supply_chain_assets`
            SET last_analyzed = CURRENT_TIMESTAMP()
            WHERE asset_id = '{asset_id}'
            """
            
            query_job = self.client.query(update_query)
            query_job.result()
            
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to update analysis timestamp: {str(e)}")
            return False
    
    def run_comprehensive_multimodal_analysis(self, asset_ids: List[str]) -> Dict[str, Any]:
        """Run comprehensive multimodal analysis on multiple assets"""
        console.print("🚀 Starting comprehensive multimodal analysis...")
        
        try:
            results = {}
            
            for asset_id in asset_ids:
                console.print(f"🔍 Analyzing asset: {asset_id}")
                results[asset_id] = self.analyze_asset_with_ai(asset_id)
            
            # Compile comprehensive report
            comprehensive_report = {
                "analysis_timestamp": time.time(),
                "assets_analyzed": len(asset_ids),
                "analysis_results": results,
                "summary": self._generate_multimodal_analysis_summary(results)
            }
            
            console.print("✅ Comprehensive multimodal analysis completed")
            return {"success": True, "data": comprehensive_report}
            
        except Exception as e:
            console.print(f"❌ Comprehensive multimodal analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_multimodal_analysis_summary(self, results: Dict[str, Any]) -> str:
        """Generate summary of multimodal analysis results"""
        successful_analyses = sum(1 for result in results.values() if result.get("success"))
        total_assets = len(results)
        
        if successful_analyses == total_assets:
            return f"Successfully analyzed all {total_assets} assets using multimodal AI"
        elif successful_analyses > 0:
            return f"Partially successful: analyzed {successful_analyses} out of {total_assets} assets"
        else:
            return f"Failed to analyze any of the {total_assets} assets"

# Global instance
multimodal_processor = MultimodalProcessor()
