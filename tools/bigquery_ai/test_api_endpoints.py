#!/usr/bin/env python3
"""
Test script for API endpoints
"""
import requests
import json

def test_api_endpoints():
    """Test the API endpoints"""
    base_url = "http://localhost:3000/api/bigquery-ai"
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Test 1: Status endpoint
    print("\n1️⃣ Testing /status endpoint...")
    try:
        response = requests.get(f"{base_url}/status")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            if data.get('success'):
                print(f"   Service Status: {data.get('data', {}).get('status', 'Unknown')}")
            else:
                print(f"   Error: {data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Costs endpoint
    print("\n2️⃣ Testing /costs endpoint...")
    try:
        response = requests.get(f"{base_url}/costs")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            if data.get('success'):
                cost_summary = data.get('data', {}).get('cost_summary', {})
                if cost_summary:
                    today = cost_summary.get('today', {})
                    print(f"   Today's Cost: ${today.get('cost_usd', 0):.4f}")
                    print(f"   Budget Remaining: ${today.get('remaining_usd', 0):.4f}")
                    print(f"   Usage: {today.get('usage_percent', 0):.1f}%")
            else:
                print(f"   Error: {data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Test endpoint
    print("\n3️⃣ Testing /test endpoint...")
    try:
        response = requests.post(f"{base_url}/test")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            if data.get('success'):
                print("   Test endpoint working")
            else:
                print(f"   Error: {data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
