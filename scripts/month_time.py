# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests"
# ]
# ///

import requests
import sys
import calendar
import json

# Constatnts
BASE_URL = "https://<YOUR_DOMAIN>/api/odata/v3.2/workLogsOnly"
API_KEY = "<YOUR_API_KEY>"
HOURS_IN_DAY = 7

# Get year and month
if len(sys.argv) >= 2:
    year = sys.argv[1]
    month = sys.argv[2] if len(sys.argv) == 3 else None
else:
    year = input("Enter the year (YYYY): ")
    month = input("Enter the month (MM) or press Enter to run for the whole year: ") or None

try:
    year = int(year)
except ValueError as e:
    print(f"Invalid year input: {e}")
    sys.exit(1)

# Fetch and display data for a given month
def fetch_data(year, month):
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01T00:00:00Z"
    end_date = f"{year}-{month:02d}-{last_day}T23:59:59Z"
    
    url = f"{BASE_URL}?$apply=filter(Timestamp ge {start_date} and Timestamp le {end_date})/aggregate(PeriodLength with sum as total)"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    try:
        data = response.json()
        total_seconds = data.get("value", [{}])[0].get("total", 0)
        total_hours = total_seconds / 3600
        total_days = total_hours / HOURS_IN_DAY
        
        print(f"Time log report for {year}-{month:02d}")
        print(f"Total time logged: {total_seconds} seconds")
        print(f"Total time logged: {total_hours:.2f} hours")
        print(f"Total time logged: {total_days:.2f} days (assuming {HOURS_IN_DAY} hours per day)")
        print("-" * 40)
    except (json.JSONDecodeError, KeyError, IndexError):
        print(f"Error parsing response data for {year}-{month:02d}")

# Run for specified month or whole year
if month:
    try:
        month = int(month)
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")
        fetch_data(year, month)
    except ValueError as e:
        print(f"Invalid month input: {e}")
        sys.exit(1)
else:
    for month in range(1, 13):
        fetch_data(year, month)
    
