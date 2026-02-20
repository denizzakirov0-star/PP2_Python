from datetime import datetime, timedelta
print("Yesterday: ", datetime.now().date() - timedelta(days=1))
print("Today: ", datetime.now().date())
print("Tomorrow", datetime.now().date() + timedelta(days=1))