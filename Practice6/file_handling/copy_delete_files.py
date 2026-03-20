import shutil
import os
# copy data to new file
shutil.copy("data.txt", "copy_data.txt")

# delete file safely
if os.path.exists("data.txt"):
    os.remove("data.txt")
else:
    print("File already deleted or doesn't exists")