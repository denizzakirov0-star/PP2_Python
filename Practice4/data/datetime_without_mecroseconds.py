from datetime import datetime
now = datetime.now()
now = now.replace(microsecond=0)
print("date without microseconds:",now)