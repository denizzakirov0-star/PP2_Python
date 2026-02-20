from datetime import datetime, timedelta
date_str1 = input("Input first data, for example '2026-02-20 15:30:00': ")
date_str2 = input("Input second data, for example '2026-02-20 14:30:00': ")
date_obj1 = datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
date_obj2 = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")
different = abs(date_obj1 - date_obj2).total_seconds()
print(different)