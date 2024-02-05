from pymongo import MongoClient
import json
import time

# Connect to MongoDB
client = MongoClient("mongodb://admin:password@localhost:27017/admin")
database_name = "iph"
collection_name = "reid"
db = client[database_name]
collection = db[collection_name]

# Load sample data from the existing JSON file
with open("sample_data_reid.json", "r") as file:
    base_sample_data = json.load(file)

# Function to increment the timestamp field by one millisecond
def increment_timestamp(sample_data):
    timestamp_ms = sample_data.get("query_time", 0)
    sample_data["query_time"] = timestamp_ms + 1
    print(f"Timestamp incremented to {sample_data['query_time']}")

# Function to insert data into MongoDB
def insert_data(sample_data):
    collection.insert_one(sample_data)
    print(f"Data inserted at {sample_data['query_time']}")

# Initial timestamp from the loaded sample data
current_timestamp = base_sample_data.get("query_time", 0)

# Continuously generate and insert data with an incremented timestamp
while True:
    new_sample = base_sample_data.copy()
    new_sample["query_time"] = current_timestamp
    increment_timestamp(new_sample)
    insert_data(new_sample)
    current_timestamp += 1  # Increment timestamp for the next iteration

