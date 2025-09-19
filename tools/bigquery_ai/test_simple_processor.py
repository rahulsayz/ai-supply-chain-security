#!/usr/bin/env python3
"""
Simple test script for the unified AI processor
"""
import sys
import os
import json

def test_basic_functionality():
    """Test basic functionality"""
    try:
        # Test basic imports
        from config import config
        print("✅ Config loaded successfully")
        print(f"   Project ID: {config.gcp_project_id}")
        
        # Test cost monitor
        from cost_monitor import get_cost_monitor
        cost_monitor = get_cost_monitor()
        print("✅ Cost monitor initialized successfully")
        
        # Test basic operations
        cost_summary = cost_monitor.get_cost_summary()
        print("✅ Cost summary retrieved successfully")
        print(f"   Today's cost: ${cost_summary['today']['cost_usd']:.4f}")
        print(f"   Budget remaining: ${cost_summary['today']['remaining_usd']:.4f}")
        
        return {
            "success": True,
            "message": "All basic functionality tests passed",
            "config": {
                "project_id": config.gcp_project_id,
                "dataset_id": config.gcp_dataset_id
            },
            "cost_summary": cost_summary
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            result = test_basic_functionality()
        elif command == "status":
            result = {
                "success": True,
                "status": "available",
                "message": "Simplified AI processor is available"
            }
        elif command == "costs":
            try:
                from cost_monitor import get_cost_monitor
                cost_monitor = get_cost_monitor()
                cost_summary = cost_monitor.get_cost_summary()
                
                # Get daily costs for last 7 days
                daily_costs = {}
                from datetime import datetime, timedelta
                today = datetime.now()
                for i in range(7):
                    date = today - timedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    daily_cost = cost_monitor.get_daily_cost(date_str)
                    daily_costs[date_str] = {
                        'cost_usd': daily_cost,
                        'usage_percent': (daily_cost / cost_summary['today']['budget_limit_usd']) * 100
                    }
                
                result = {
                    "success": True,
                    "cost_summary": cost_summary,
                    "daily_costs": daily_costs
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e)
                }
        else:
            result = {
                "success": False,
                "error": f"Unknown command: {command}"
            }
    else:
        result = test_basic_functionality()
    
    # Output as JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
