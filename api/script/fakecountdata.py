from pymongo import MongoClient
from datetime import datetime, timedelta
import random
from concurrent.futures import ProcessPoolExecutor
import uuid
import pytz

# Connect to MongoDB
client = MongoClient('mongodb://admin:password@localhost:27017/?authSource=admin')
db = client['iph']
collection = db['count_per_hour']


# Function to generate a random document
def generate_random_document(start_time):
    document = {
        "_id": str(uuid.uuid4()),
        "start_time": start_time.isoformat(),
        "camera_counts": {f"camera_id_{i}": random.randint(1, 50) for i in range(1, 4)},
        "count": 0,  # Placeholder for count, will be updated below
        "end_time": (start_time + timedelta(hours=1)).isoformat()
    }
    document["count"] = sum(document["camera_counts"].values())
    return document

# Date range from 1/1/2023 to 1/1/2025 in GMT
start_date_gmt = datetime(2023, 1, 1, tzinfo=pytz.utc)
end_date_gmt = datetime(2025, 1, 1, tzinfo=pytz.utc)

# Convert to GMT+7
timezone_gmt7 = pytz.timezone('Asia/Bangkok')
start_date = start_date_gmt.astimezone(timezone_gmt7)
end_date = end_date_gmt.astimezone(timezone_gmt7)

# Function to generate and insert documents for a specific hour
def generate_and_insert_document(current_date):
    document = generate_random_document(current_date)
    collection.insert_one(document)
    print(f"Inserted document for {current_date.isoformat()} to {(current_date + timedelta(hours=1)).isoformat()}")

# Use ProcessPoolExecutor for parallel execution
with ProcessPoolExecutor() as executor:
    # Generate and insert documents for each hour concurrently
    executor.map(generate_and_insert_document, [start_date + timedelta(hours=i) for i in range(int((end_date - start_date).total_seconds() // 3600))])

# Close the MongoDB connection
client.close()