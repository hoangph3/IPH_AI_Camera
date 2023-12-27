from pymongo import MongoClient
from datetime import datetime, timedelta
import schedule
import time

# MongoDB connection details
mongo_uri = 'mongodb://admin:password@localhost:27017/?authSource=admin'
database_name = 'iph'
source_collection_name = 'reid'
target_collection_name = 'count_per_hour'

def run_analysis():
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[database_name]
    source_collection = db[source_collection_name]
    target_collection = db[target_collection_name]

    # Calculate the start and end times for the previous hour
    current_time = datetime.utcnow()
    end_date = datetime(current_time.year, current_time.month, current_time.day, current_time.hour, 0, 0)
    start_date = end_date - timedelta(hours=1)

    # Perform aggregation for the previous hour
    result = source_collection.aggregate([
        {
            '$match': {
                'query_time': {
                    '$gte': start_date,
                    '$lt': end_date
                }
            }
        },
        {
            '$group': {
                '_id': '$cam_id',
                'count': {'$sum': 1}
            }
        }
        # Add more stages for additional aggregations if needed
    ])

    # Process the result for the previous hour
    count_data = {
        'start_time': start_date,
        'end_time': end_date,
        'camera_counts': []
    }

    for hour_data in result:
        count_data['camera_counts'].append({
            f'camera_id_{hour_data["_id"]}': hour_data['count']
        })

    # Save the result to the new collection
    target_collection.insert_one(count_data)
    print(f'Analysis for {start_date} to {end_date} saved to {target_collection_name}')

# Run the analysis immediately for testing purposes
run_analysis()
