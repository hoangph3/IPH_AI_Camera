from pymongo import MongoClient


def print_smallest_timestamp(
    db_name, collection_name, mongo_uri="mongodb://admin:password@localhost:27017/admin"
):
    """
    Finds and prints the smallest "timestamp" from the specified MongoDB collection.
    
    Args:
    db_name (str): Name of the database.
    collection_name (str): Name of the collection.
    mongo_uri (str): MongoDB connection URI.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Find the document with the smallest timestamp
    document = collection.find_one(
        {
            "query_time": {"$exists": True, "$ne": None}
        },  # Ensure the query_time exists and is not None
        sort=[("query_time", 1)],  # Sort by timestamp in ascending order
        projection={
            "query_time": 1,
            "_id": 0,
        },  # Only include the query_time field in the result
    )

    if document:
        print("Smallest query_time:")
        print(document.get("query_time"))
    else:
        print("No document found with a valid query_time.")


# Usage
print_smallest_timestamp(db_name="iph", collection_name="reid")
