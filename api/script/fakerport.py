import pymongo

from datetime import datetime, timedelta
import random


def split_time(start_time, end_time, batch_time):
    time_boxes = []

    current_time = start_time
    while current_time < end_time:
        next_time = current_time + batch_time
        if next_time > end_time:
            next_time = end_time

        time_boxes.append((current_time, next_time))
        current_time = next_time

    return time_boxes


# Connect to MongoDB
client = pymongo.MongoClient(
    "mongodb://admin:password@localhost:27017/admin"
)  # Replace with your MongoDB connection string
db = client["iph"]  # Replace with your database name
collection = db["report_test"]  # Replace with your collection name

# Dictionary to push
time_boxes = split_time(
    start_time=datetime(2022, 12, 15, 0, 0, 0),
    end_time=datetime(2024, 12, 30, 23, 59, 59),
    batch_time=timedelta(hours=1),
)
for time_box in time_boxes:
    datetime_from, datetime_to = time_box
    doc = {
        "start_time": datetime_from,
        "end_time": datetime_to,
        "camera_counts": {
            k: random.randint(0, 100) for k in [f"Cam{i}" for i in range(21)]
        },
    }
    doc["count"] = sum(list(doc["camera_counts"].values()))
    # Insert the dictionary into the collection
    collection.insert_one(doc)

print("Dictionary inserted successfully.")
