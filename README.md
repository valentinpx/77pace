# 77pace
This project contains a set of tools to work with the 7pace Timetracker tool.

## Tools
### Chrome Extension
#### Usage
This project is a Google Chrome extension that displays the number of days passed in the 7-pace calendar.
![extension_calendar](https://raw.githubusercontent.com/valentinpx/77pace/refs/heads/main/img/extension_calendar.png)
The days of each month are stored in the browser, you can view a recap in the popup.
![extension_popup](https://raw.githubusercontent.com/valentinpx/77pace/refs/heads/main/img/extension_popup.png)

#### Installation
Toggle the developer mode in [chrome://extensions](chrome://extensions). and load the extension as an unpacked extension.
![extension_install](https://raw.githubusercontent.com/valentinpx/77pace/refs/heads/main/img/extension_install.png)

### month_time.py script
#### Usage
This script is used to fetch the total time spent in a month or a year. It uses the 7pace Timetracker API to get the data.
```
Time log report for 2025-01
Total time logged: 425730 seconds
Total time logged: 118.26 hours
Total time logged: 16.89 days (assuming 7 hours per day)
----------------------------------------
Time log report for 2025-02
Total time logged: 424642 seconds
Total time logged: 117.96 hours
Total time logged: 16.85 days (assuming 7 hours per day)
----------------------------------------
Time log report for 2025-03
Total time logged: 262589 seconds
Total time logged: 72.94 hours
Total time logged: 10.42 days (assuming 7 hours per day)
----------------------------------------
```

First, specify the following constants in the script:
```python
BASE_URL = "https://<YOUR_DOMAIN>/api/odata/v3.2/workLogsOnly"
API_KEY = "<YOUR_API_KEY>"
HOURS_IN_DAY = 7
```

Run the script with the following command:
```bash
uv run month_time.py <year> <month (optional)>
```
