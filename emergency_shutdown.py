#!/usr/bin/env python3
"""
EMERGENCY SHUTDOWN - Run this if costs are spiraling
"""

import os
import sys
import json
from datetime import datetime

print("🚨 EMERGENCY SHUTDOWN INITIATED 🚨")
print("=" * 50)

# Create shutdown flag
with open('EMERGENCY_SHUTDOWN.flag', 'w') as f:
    f.write(f"EMERGENCY SHUTDOWN at {datetime.now()}\n")
    f.write("All processing halted\n")
    f.write("Check costs/usage_tracking.json for details\n")

# Set environment variables to disable everything
env_file = '.env.emergency'
with open(env_file, 'w') as f:
    f.write("# EMERGENCY SHUTDOWN - ALL SYSTEMS DISABLED\n")
    f.write("DISABLE_ALL_AI=true\n")
    f.write("MOCK_MODE=true\n")
    f.write("MAX_DAILY_COST=0.00\n")
    f.write("EMERGENCY_SHUTDOWN=true\n")
    f.write("LLM_MODE=mock\n")

# Try to read cost data
try:
    with open('echo-backend/costs/usage_tracking.json', 'r') as f:
        costs = json.load(f)
        print(f"\nTotal costs incurred: ${costs.get('total', 0):.2f}")
        
        # Show daily costs
        print("\nDaily costs:")
        for date, cost in sorted(costs.get('daily', {}).items())[-7:]:
            print(f"  {date}: ${cost:.2f}")
            
        print(f"\nMonthly total: ${list(costs.get('monthly', {}).values())[-1]:.2f}")
except:
    print("\nCould not read cost tracking file")

print("\n✅ EMERGENCY SHUTDOWN COMPLETE")
print("\nTo resume operations:")
print("1. Check your API provider dashboards")
print("2. Review costs/usage_tracking.json")
print("3. Delete EMERGENCY_SHUTDOWN.flag")
print("4. Update .env with new limits")
print("5. Consider using local models instead")

# Stop any running processes
print("\nAttempting to stop services...")
os.system("pkill -f 'python.*main.py'")
os.system("pkill -f 'node.*dev'")

print("\n🛑 All services stopped")
print("💰 Check your billing immediately!")