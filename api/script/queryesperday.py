import pymongo
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import schedule
import time
from elasticsearch.helpers import scan
import pytz

# Connect to MongoDB
client = pymongo.MongoClient(
    "mongodb://root:password@localhost:27017/?authSource=admin"
)  # Replace with your actual MongoDB connection URI
database_name = "api_test"
collection_name = "count_per_day"
collection = client[database_name][collection_name]

# Connect to Elasticsearch
es = Elasticsearch()
index_name = "kotora_api_test"  # Replace with your actual index name


def query_and_save_per_day():
    try:
        local_tz = pytz.timezone(
            "Asia/Bangkok"
        )  # Replace 'Asia/Bangkok' with your local timezone
        current_time = datetime.now(local_tz)

        # Define the start time and end time for the current day
        start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1) - timedelta(microseconds=1)

        # Convert the start and end times to UNIX timestamps
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        unique_global_ids = set()
        scroll = scan(
            es,
            query={
                "query": {
                    "range": {
                        "timestamp": {"gte": start_timestamp, "lt": end_timestamp}
                    }
                }
            },
            index=index_name,
            scroll="2m",
            size=1000,
        )

        for result in scroll:
            unique_global_ids.add(result["_source"]["global_id"])

        # Save the count to MongoDB
        count_data = {
            "start_time": start_time,
            "end_time": end_time,
            "count": len(unique_global_ids),
        }
        collection.replace_one(
            {"start_time": start_time, "end_time": end_time}, count_data, upsert=True
        )

        # Check if the data has been inserted
        print(f"Data inserted into MongoDB: {count_data}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Schedule the query_and_save_per_day function to run once a day
schedule.every().day.do(query_and_save_per_day)

while True:
    schedule.run_pending()
    time.sleep(1)
