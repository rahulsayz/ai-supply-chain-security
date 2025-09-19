"""
Configuration module for BigQuery AI processing
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class BigQueryAIConfig(BaseSettings):
    """Configuration for BigQuery AI processing"""
    
    # GCP Configuration
    gcp_project_id: str = Field(..., validation_alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="US", alias="GCP_LOCATION")
    gcp_dataset_id: str = Field(default="supply_chain_ai", alias="GCP_DATASET_ID")
    
    # Service Account
    google_application_credentials: str = Field(..., alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Cost Controls
    daily_budget_limit_usd: float = Field(default=5.0, alias="DAILY_BUDGET_LIMIT_USD")
    max_query_cost_usd: float = Field(default=1.0, alias="MAX_QUERY_COST_USD")
    max_processing_mb: int = Field(default=100, alias="MAX_PROCESSING_MB")
    query_timeout_seconds: int = Field(default=30, alias="QUERY_TIMEOUT_SECONDS")
    
    # AI Model Configuration
    ai_model: str = Field(default="gemini-1.5-flash", alias="AI_MODEL")
    max_tokens: int = Field(default=1000, alias="MAX_TOKENS")
    
    # Processing Configuration
    batch_size: int = Field(default=10, alias="BATCH_SIZE")
    enable_vector_search: bool = Field(default=True, alias="ENABLE_VECTOR_SEARCH")
    enable_multimodal: bool = Field(default=True, alias="ENABLE_MULTIMODAL")
    
    # Output Configuration
    output_data_path: str = Field(default="../data", alias="OUTPUT_DATA_PATH")
    enable_live_mode: bool = Field(default=True, alias="ENABLE_LIVE_MODE")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

class CostTrackerConfig(BaseSettings):
    """Configuration for cost tracking"""
    
    # Cost thresholds
    warning_threshold_percent: float = Field(default=80.0, alias="WARNING_THRESHOLD_PERCENT")
    critical_threshold_percent: float = Field(default=95.0, alias="CRITICAL_THRESHOLD_PERCENT")
    
    # Monitoring
    cost_check_interval_minutes: int = Field(default=15, alias="COST_CHECK_INTERVAL_MINUTES")
    enable_cost_alerts: bool = Field(default=True, alias="ENABLE_COST_ALERTS")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

# Global configuration instances
config = BigQueryAIConfig()
cost_config = CostTrackerConfig()

def validate_config() -> bool:
    """Validate configuration and return True if valid"""
    try:
        # Check required environment variables
        if not config.gcp_project_id:
            print("❌ GCP_PROJECT_ID is required")
            return False
            
        if not config.google_application_credentials:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS is required")
            return False
            
        # Check if service account file exists
        if not os.path.exists(config.google_application_credentials):
            print(f"❌ Service account file not found: {config.google_application_credentials}")
            return False
            
        # Validate cost limits
        if config.daily_budget_limit_usd <= 0:
            print("❌ Daily budget limit must be positive")
            return False
            
        if config.max_query_cost_usd <= 0:
            print("❌ Max query cost must be positive")
            return False
            
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def print_config_summary():
    """Print configuration summary"""
    print("\n🔧 BigQuery AI Configuration Summary")
    print("=" * 50)
    print(f"GCP Project: {config.gcp_project_id}")
    print(f"GCP Location: {config.gcp_location}")
    print(f"Dataset: {config.gcp_dataset_id}")
    print(f"Daily Budget: ${config.daily_budget_limit_usd}")
    print(f"Max Query Cost: ${config.max_query_cost_usd}")
    print(f"Max Processing: {config.max_processing_mb}MB")
    print(f"Query Timeout: {config.query_timeout_seconds}s")
    print(f"AI Model: {config.ai_model}")
    print(f"Vector Search: {'✅' if config.enable_vector_search else '❌'}")
    print(f"Multimodal: {'✅' if config.enable_multimodal else '❌'}")
    print(f"Live Mode: {'✅' if config.enable_live_mode else '❌'}")
    print("=" * 50)
