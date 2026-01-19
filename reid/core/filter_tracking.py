from pymongo import MongoClient


def delete_documents_without_valid_timestamp(
    db_name, collection_name, mongo_uri="mongodb://admin:password@localhost:27017/admin"
):
    """
    Deletes documents from the specified MongoDB collection that do not have a "timestamp" field or have a "timestamp" field set to None.
    
    Args:
    db_name (str): Name of the database.
    collection_name (str): Name of the collection.
    mongo_uri (str): MongoDB connection URI.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Ensure an index on the "timestamp" field
    collection.create_index("query_time")

    # Delete documents without the "query_time" field or with "query_time" set to None
    delete_result = collection.delete_many(
        {"$or": [{"query_time": {"$exists": False}}, {"query_time": None}]}
    )

    print(
        f"Deleted {delete_result.deleted_count} documents without 'query_time' field or with 'query_time' set to None."
    )


# Usage
delete_documents_without_valid_timestamp(db_name="iph", collection_name="reid")
