import pymongo
from datetime import datetime
from dateutil.relativedelta import relativedelta
import schedule
import time

# Connect to MongoDB
client = pymongo.MongoClient(
    "mongodb://root:password@localhost:27017/?authSource=admin"
)  # Replace with your actual MongoDB connection URI
database_name = "api_test"
daily_collection_name = "count_per_day"
monthly_collection_name = "count_per_month"
daily_collection = client[database_name][daily_collection_name]
monthly_collection = client[database_name][monthly_collection_name]


def calculate_monthly_count(year, month):
    try:
        start_date = datetime(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)

        pipeline = [
            {"$match": {"start_time": {"$gte": start_date, "$lte": end_date}}},
            {
                "$group": {
                    "_id": None,
                    "total_count": {"$sum": "$count"},
                    "camera_counts": {"$mergeObjects": "$camera_counts"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "start_time": start_date,
                    "end_time": end_date,
                    "count": "$total_count",
                    "camera_counts": "$camera_counts",
                }
            },
        ]

        result = list(daily_collection.aggregate(pipeline))
        if result:
            monthly_data = result[0]
            monthly_collection.replace_one(
                {"start_time": start_date, "end_time": end_date},
                monthly_data,
                upsert=True,
            )
            print(f"Data inserted into MongoDB for {year}-{month}: {monthly_data}")
        else:
            print(f"No data found for {year}-{month}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Schedule the script to run at the beginning of each month
def job():
    current_time = datetime.now()
    year = current_time.year
    month = current_time.month
    calculate_monthly_count(year, month)


schedule.every().month.at("00:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
