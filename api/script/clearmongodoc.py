import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://root:password@localhost:27017/?authSource=admin")  # Replace with your actual MongoDB connection URI
database_name = "api_test"
collection_name = "cam_list"
collection = client[database_name][collection_name]

# Clear all documents from the collection
result = collection.delete_many({})

# Print the result to confirm the deletion
print(f"{result.deleted_count} documents deleted from the collection.")

# Check if the collection is empty
print(list(collection.find()))
