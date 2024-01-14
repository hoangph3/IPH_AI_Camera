from datetime import datetime
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://admin:password@localhost:27017/admin")
database_name = "iph"
collection_name_hour = "report_test"
db = client[database_name]

# Define the query
query = {
    'start_time': {'$gte': datetime(2023, 12, 29, 12, 0)},
    'end_time': {'$lte': datetime(2023, 12, 29, 13, 0)}
}

# Execute the query
result = db[collection_name_hour].find(query)

# Print the results or perform any other actions
for document in result:
    print(document)

# Close the MongoDB connection when you're done
client.close()
