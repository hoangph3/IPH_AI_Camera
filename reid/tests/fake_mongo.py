import pymongo
from utility import handler
from datetime import datetime, timedelta
import random


# Connect to MongoDB
client = pymongo.MongoClient("mongodb://admin:password@localhost:27017/admin")  # Replace with your MongoDB connection string
db = client["iph"]  # Replace with your database name
collection = db["report"]  # Replace with your collection name

# Dictionary to push
time_boxes = handler.split_time(
    start_time=datetime(2023, 12, 15, 0, 0, 0),
    end_time=datetime(2023, 12, 30, 23, 59, 59),
    batch_time=timedelta(hours=1)
)
for time_box in time_boxes:
    datetime_from, datetime_to = time_box
    doc = {
        'start_time': datetime_from,
        'end_time': datetime_to,
        'camera_counts': {k: random.randint(0, 100) for k in [
            f"c{i}" for i in range(21)
        ]}
    }
    doc['count'] = sum(list(doc['camera_counts'].values()))
    # Insert the dictionary into the collection
    collection.insert_one(doc)

print("Dictionary inserted successfully.")
