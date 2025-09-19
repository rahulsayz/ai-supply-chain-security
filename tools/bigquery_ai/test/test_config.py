#!/usr/bin/env python3
"""
Test configuration loading
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv('../.env')

class TestConfig(BaseSettings):
    """Test configuration"""
    gcp_project_id: str = Field(..., alias="GCP_PROJECT_ID")
    google_application_credentials: str = Field(..., alias="GOOGLE_APPLICATION_CREDENTIALS")
    
    class Config:
        env_file = "../.env"
        case_sensitive = False
        extra = "ignore"

if __name__ == "__main__":
    try:
        config = TestConfig()
        print("✅ Configuration loaded successfully!")
        print(f"GCP Project ID: {config.gcp_project_id}")
        print(f"Service Account Path: {config.google_application_credentials}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        print(f"Environment variables:")
        print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID')}")
        print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
