#!/usr/bin/env python3
"""
Minimal test for Pydantic configuration
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv('../.env')

print("Environment variables loaded:")
print(f"GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

class MinimalConfig(BaseSettings):
    gcp_project_id: str
    google_application_credentials: str
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

if __name__ == "__main__":
    try:
        config = MinimalConfig()
        print("✅ Configuration loaded successfully!")
        print(f"GCP Project ID: {config.gcp_project_id}")
        print(f"Service Account Path: {config.google_application_credentials}")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        print(f"Type: {type(e)}")
        if hasattr(e, 'errors'):
            for error in e.errors():
                print(f"  - {error}")
