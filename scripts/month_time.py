# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
#     "python-dotenv"
# ]
# ///

import requests
import sys
import calendar
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Constants
ENDPOINT_PATH = "/api/odata/v3.2/workLogsWorkItems"

# Load environment variables from .env file
def load_environment(env_path=None):
    if env_path:
        env_file = Path(env_path)
        if not env_file.is_file():
            print(f"Specified .env file '{env_path}' does not exist.")
            sys.exit(1)
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()

    api_key = os.getenv("API_KEY")
    if not api_key:
        print("API_KEY not found in environment variables.")
        sys.exit(1)

    try:
        hours_in_day = float(os.getenv("HOURS_IN_DAY", "7"))
    except ValueError:
        print("Invalid HOURS_IN_DAY in environment. It must be a number.")
        sys.exit(1)

    base_domain = os.getenv("BASE_DOMAIN")
    if not base_domain.startswith("http"):
        print("BASE_DOMAIN must start with http:// or https://")
        sys.exit(1)

    return api_key, hours_in_day, base_domain

# Fetch and display data for a given month
def fetch_data(year, month, api_key, hours_in_day, base_domain):
    base_url = f"{base_domain.rstrip('/')}{ENDPOINT_PATH}"
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01T00:00:00Z"
    end_date = f"{year}-{month:02d}-{last_day}T23:59:59Z"

    url = (
        f"{base_url}?"
        f"$apply=filter(Timestamp ge {start_date} and Timestamp le {end_date})/"
        f"groupby((WorkItem/System_TeamProject),aggregate(PeriodLength with sum as TotalTime))"
        f"&worklogsFilter=User/Email eq '{os.getenv('USER_EMAIL')}'"
    )
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    print(url)
    try:
        data = response.json()
        print(f"Time log report for {year}-{month:02d}")
        total_seconds_all = 0
        for item in data.get("value", []):
            work_item = item.get("WorkItem")
            if isinstance(work_item, dict):
                project_name = work_item.get("System_TeamProject", "Unknown Project")
            else:
                project_name = "Unknown Project"
            total_seconds = item.get("TotalTime", 0)
            total_hours = total_seconds / 3600
            total_seconds_all += total_seconds
            print(f"Time logged for project {project_name}: {total_seconds}s, {total_hours:.2f}h")
        total_hours_all = total_seconds_all / 3600
        total_days_all = total_hours_all / hours_in_day
        print(f"Total time logged across all projects: {total_seconds_all} seconds")
        print(f"Total time logged across all projects: {total_hours_all:.2f} hours")
        print(f"Total time logged across all projects: {total_days_all:.2f} days (assuming {hours_in_day} hours per day)")
        print("-" * 40)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing response data for {year}-{month:02d}: {e}")

# Main execution
def main():
    args = sys.argv[1:]
    env_path = None

    if '--env' in args:
        env_index = args.index('--env')
        try:
            env_path = args[env_index + 1]
            args = args[:env_index] + args[env_index + 2:]
        except IndexError:
            print("Error: --env flag provided but no path specified.")
            sys.exit(1)

    api_key, hours_in_day, base_domain = load_environment(env_path)

    if len(args) >= 1:
        year = args[0]
        month = args[1] if len(args) >= 2 else None
    else:
        year = input("Enter the year (YYYY): ")
        month = input("Enter the month (MM) or press Enter to run for the whole year: ") or None

    try:
        year = int(year)
    except ValueError as e:
        print(f"Invalid year input: {e}")
        sys.exit(1)

    if month:
        try:
            month = int(month)
            if month < 1 or month > 12:
                raise ValueError("Month must be between 1 and 12.")
            fetch_data(year, month, api_key, hours_in_day, base_domain)
        except ValueError as e:
            print(f"Invalid month input: {e}")
            sys.exit(1)
    else:
        for month in range(1, 13):
            fetch_data(year, month, api_key, hours_in_day, base_domain)

if __name__ == "__main__":
    main()
