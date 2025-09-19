"""
Vector Processor - Implements vectorization and semantic search for supply chain threats
"""
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import bigframes as bf
from bigframes.ml.llm import TextEmbeddingGenerator

from config import config
from cost_monitor import get_cost_monitor

console = Console()

class VectorProcessor:
    """Comprehensive vector processor for semantic search and similarity analysis"""
    
    def __init__(self):
        self.client = bigquery.Client(project=config.gcp_project_id)
        self.cost_monitor = get_cost_monitor()
        self.session = bf.get_global_session()
        
    def generate_embeddings_for_threats(self) -> Dict[str, Any]:
        """Generate embeddings for all threat descriptions using ML.GENERATE_EMBEDDING"""
        query = f"""
        UPDATE `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
        SET embedding = ML.GENERATE_EMBEDDING('textembedding-gecko@003', description)
        WHERE embedding IS NULL
        """
        
        return self._execute_vector_query(query, "embedding_generation")
    
    def generate_embeddings_for_vendors(self) -> Dict[str, Any]:
        """Generate embeddings for vendor descriptions"""
        query = f"""
        UPDATE `{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects`
        SET embedding = ML.GENERATE_EMBEDDING('textembedding-gecko@003', description)
        WHERE embedding IS NULL
        """
        
        return self._execute_vector_query(query, "vendor_embedding_generation")
    
    def create_vector_indexes(self) -> Dict[str, Any]:
        """Create vector indexes for fast similarity search"""
        results = {}
        
        # Create vector index for threats
        threat_index_query = f"""
        CREATE VECTOR INDEX threat_vector_index 
        ON `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`(embedding) 
        OPTIONS(
            distance_type='COSINE',
            index_type='IVF',
            num_clusters=100
        )
        """
        
        results["threat_index"] = self._execute_vector_query(threat_index_query, "threat_vector_index_creation")
        
        # Create vector index for vendors
        vendor_index_query = f"""
        CREATE VECTOR INDEX vendor_vector_index 
        ON `{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects`(embedding) 
        OPTIONS(
            distance_type='COSINE',
            index_type='IVF',
            num_clusters=50
        )
        """
        
        results["vendor_index"] = self._execute_vector_query(vendor_index_query, "vendor_vector_index_creation")
        
        return results
    
    def perform_vector_search(self, query_text: str, search_type: str = "threats", top_k: int = 5) -> Dict[str, Any]:
        """Perform vector similarity search using VECTOR_SEARCH"""
        
        if search_type == "threats":
            search_query = f"""
            SELECT 
                report_id,
                vendor_name,
                threat_type,
                severity,
                description,
                VECTOR_SEARCH(
                    'threat_vector_index',
                    embedding,
                    ML.GENERATE_EMBEDDING('textembedding-gecko@003', '{query_text}'),
                    {top_k}
                ) AS similarity_score
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
            WHERE embedding IS NOT NULL
            ORDER BY similarity_score DESC
            LIMIT {top_k}
            """
        else:  # vendors
            search_query = f"""
            SELECT 
                object_id,
                vendor_id,
                object_type,
                description,
                risk_score,
                VECTOR_SEARCH(
                    'vendor_vector_index',
                    embedding,
                    ML.GENERATE_EMBEDDING('textembedding-gecko@003', '{query_text}'),
                    {top_k}
                ) AS similarity_score
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects`
            WHERE embedding IS NOT NULL
            ORDER BY similarity_score DESC
            LIMIT {top_k}
            """
        
        return self._execute_vector_query(search_query, f"vector_search_{search_type}")
    
    def find_similar_threats(self, threat_description: str, top_k: int = 5) -> Dict[str, Any]:
        """Find similar threats based on description similarity"""
        search_query = f"""
        SELECT 
            t1.report_id,
            t1.vendor_name,
            t1.threat_type,
            t1.severity,
            t1.description,
            VECTOR_SEARCH(
                'threat_vector_index',
                t1.embedding,
                t2.embedding,
                {top_k}
            ) AS similarity_score
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports` t1
        CROSS JOIN (
            SELECT ML.GENERATE_EMBEDDING('textembedding-gecko@003', '{threat_description}') as embedding
        ) t2
        WHERE t1.embedding IS NOT NULL
        ORDER BY similarity_score DESC
        LIMIT {top_k}
        """
        
        return self._execute_vector_query(search_query, "similar_threats_search")
    
    def find_similar_vendors(self, vendor_description: str, top_k: int = 5) -> Dict[str, Any]:
        """Find similar vendors based on description similarity"""
        search_query = f"""
        SELECT 
            v1.object_id,
            v1.vendor_id,
            v1.object_type,
            v1.description,
            v1.risk_score,
            VECTOR_SEARCH(
                'vendor_vector_index',
                v1.embedding,
                v2.embedding,
                {top_k}
            ) AS similarity_score
        FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.infrastructure_objects` v1
        CROSS JOIN (
            SELECT ML.GENERATE_EMBEDDING('textembedding-gecko@003', '{vendor_description}') as embedding
        ) v2
        WHERE v1.embedding IS NOT NULL
        ORDER BY similarity_score DESC
        LIMIT {top_k}
        """
        
        return self._execute_vector_query(search_query, "similar_vendors_search")
    
    def perform_semantic_clustering(self, cluster_count: int = 5) -> Dict[str, Any]:
        """Perform semantic clustering of threats using vector embeddings"""
        clustering_query = f"""
        WITH threat_embeddings AS (
            SELECT 
                report_id,
                vendor_name,
                threat_type,
                severity,
                description,
                embedding
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
            WHERE embedding IS NOT NULL
        ),
        clusters AS (
            SELECT 
                *,
                ML.KMEANS(
                    embedding,
                    {cluster_count},
                    distance_type='COSINE'
                ) OVER() AS cluster_id
            FROM threat_embeddings
        )
        SELECT 
            cluster_id,
            COUNT(*) as threat_count,
            AVG(CAST(severity AS FLOAT64)) as avg_severity,
            STRING_AGG(DISTINCT threat_type, ', ') as threat_types,
            STRING_AGG(DISTINCT vendor_name, ', ') as vendors,
            AVG(CAST(ML.GENERATE_EMBEDDING('textembedding-gecko@003', 
                CONCAT('Cluster ', CAST(cluster_id AS STRING), ' threats: ', 
                       STRING_AGG(description, ' | '))) AS FLOAT64)) as cluster_embedding
        FROM clusters
        GROUP BY cluster_id
        ORDER BY avg_severity DESC
        """
        
        return self._execute_vector_query(clustering_query, "semantic_clustering")
    
    def generate_embedding_analytics(self) -> Dict[str, Any]:
        """Generate analytics based on vector embeddings"""
        analytics_query = f"""
        WITH embedding_stats AS (
            SELECT 
                vendor_name,
                threat_type,
                severity,
                embedding,
                ML.GENERATE_EMBEDDING('textembedding-gecko@003', 
                    CONCAT('Analyze threat pattern for ', vendor_name, ': ', threat_type)) as analysis_embedding
            FROM `{config.gcp_project_id}.{config.gcp_dataset_id}.demo_threat_reports`
            WHERE embedding IS NOT NULL
        ),
        similarity_analysis AS (
            SELECT 
                vendor_name,
                threat_type,
                severity,
                VECTOR_SEARCH(
                    'threat_vector_index',
                    embedding,
                    analysis_embedding,
                    3
                ) AS top_similarities
            FROM embedding_stats
        )
        SELECT 
            vendor_name,
            threat_type,
            severity,
            top_similarities,
            AI.GENERATE_TEXT(
                'Based on this threat pattern, what are the key risk indicators and recommended mitigation strategies?',
                CONCAT('Vendor: ', vendor_name, ', Threat: ', threat_type, ', Severity: ', CAST(severity AS STRING))
            ) AS risk_analysis
        FROM similarity_analysis
        ORDER BY severity DESC
        LIMIT 10
        """
        
        return self._execute_vector_query(analytics_query, "embedding_analytics")
    
    def perform_bigframes_vector_operations(self, text_data: List[str]) -> Dict[str, Any]:
        """Perform vector operations using BigFrames TextEmbeddingGenerator"""
        try:
            console.print("🔍 Performing BigFrames vector operations...")
            start_time = time.time()
            
            # Create DataFrame with text data
            df = self.session.create_dataframe(text_data, columns=["text"])
            
            # Generate embeddings using TextEmbeddingGenerator
            embedding_gen = TextEmbeddingGenerator()
            embeddings = embedding_gen.generate(df["text"])
            
            # Add embeddings to DataFrame
            df_with_embeddings = df.assign(embedding=embeddings)
            
            # Perform similarity calculations
            similarity_results = []
            for i, row in df_with_embeddings.iterrows():
                for j, other_row in df_with_embeddings.iterrows():
                    if i != j:
                        # Calculate cosine similarity
                        similarity = self._calculate_cosine_similarity(
                            row["embedding"], 
                            other_row["embedding"]
                        )
                        similarity_results.append({
                            "text1": row["text"],
                            "text2": other_row["text"],
                            "similarity": similarity
                        })
            
            processing_time = time.time() - start_time
            
            # Sort by similarity
            similarity_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            console.print(f"✅ BigFrames vector operations completed in {processing_time:.2f}s")
            
            return {
                "success": True,
                "data": {
                    "embeddings_generated": len(text_data),
                    "similarity_pairs": similarity_results[:10],  # Top 10 most similar
                    "processing_time": processing_time
                }
            }
            
        except Exception as e:
            console.print(f"❌ BigFrames vector operations failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception:
            return 0.0
    
    def _execute_vector_query(self, query: str, query_type: str) -> Dict[str, Any]:
        """Execute vector query with cost monitoring and error handling"""
        start_time = time.time()
        
        try:
            console.print(f"🔍 Executing {query_type} query...")
            
            # Configure query job
            job_config = QueryJobConfig(
                use_query_cache=False,  # Disable cache for vector queries
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
            
            # Estimate cost for vector operations
            estimated_cost = self._estimate_vector_query_cost(query_type, processing_time)
            
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
    
    def _estimate_vector_query_cost(self, query_type: str, processing_time: float) -> float:
        """Estimate cost for vector queries based on type and processing time"""
        # Base costs for different vector operation types
        base_costs = {
            "embedding_generation": 0.0005,      # ML.GENERATE_EMBEDDING
            "vector_index_creation": 0.001,      # CREATE VECTOR INDEX
            "vector_search": 0.0003,             # VECTOR_SEARCH
            "semantic_clustering": 0.002,        # ML.KMEANS + VECTOR_SEARCH
            "embedding_analytics": 0.003,        # Complex vector operations
            "similar_threats_search": 0.0003,    # VECTOR_SEARCH
            "similar_vendors_search": 0.0003     # VECTOR_SEARCH
        }
        
        base_cost = base_costs.get(query_type, 0.0005)
        
        # Add time-based cost
        time_multiplier = min(processing_time / 5.0, 3.0)  # Cap at 3x
        
        return base_cost * time_multiplier
    
    def run_comprehensive_vector_analysis(self, query_text: str) -> Dict[str, Any]:
        """Run comprehensive vector analysis including search, clustering, and analytics"""
        console.print("🚀 Starting comprehensive vector analysis...")
        
        try:
            results = {
                "threat_search": self.perform_vector_search(query_text, "threats", 10),
                "vendor_search": self.perform_vector_search(query_text, "vendors", 10),
                "semantic_clustering": self.perform_semantic_clustering(5),
                "embedding_analytics": self.generate_embedding_analytics()
            }
            
            # Compile comprehensive report
            comprehensive_report = {
                "query_text": query_text,
                "analysis_timestamp": time.time(),
                "vector_analysis_results": results,
                "summary": self._generate_vector_analysis_summary(results)
            }
            
            console.print("✅ Comprehensive vector analysis completed")
            return {"success": True, "data": comprehensive_report}
            
        except Exception as e:
            console.print(f"❌ Comprehensive vector analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _generate_vector_analysis_summary(self, results: Dict[str, Any]) -> str:
        """Generate summary of vector analysis results"""
        summary_parts = []
        
        if results.get("threat_search", {}).get("success"):
            threat_count = len(results["threat_search"]["data"])
            summary_parts.append(f"Found {threat_count} similar threats")
        
        if results.get("vendor_search", {}).get("success"):
            vendor_count = len(results["vendor_search"]["data"])
            summary_parts.append(f"Found {vendor_count} similar vendors")
        
        if results.get("semantic_clustering", {}).get("success"):
            cluster_count = len(results["semantic_clustering"]["data"])
            summary_parts.append(f"Identified {cluster_count} threat clusters")
        
        if summary_parts:
            return "Vector analysis completed: " + "; ".join(summary_parts)
        else:
            return "Vector analysis completed with limited results"

# Global instance
vector_processor = VectorProcessor()
