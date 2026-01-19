from datetime import datetime, timedelta
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://admin:password@localhost:27017/?authSource=admin")
database_name = "iph"
collection_name_hour = "report_test"
db = client[database_name]

# Define the time range
start_timestamp = datetime(2023, 12, 29, 0, 0, 0) - timedelta(hours=7)
end_timestamp = datetime(2023, 12, 29, 2, 0, 0) - timedelta(hours=7)

# Query MongoDB
cursor = db[collection_name_hour].find(
    {"start_time": {"$gte": start_timestamp, "$lt": end_timestamp}}
)

# Print documents
for document in cursor:
    print(document)
