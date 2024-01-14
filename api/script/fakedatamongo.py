import pymongo
from datetime import datetime, timedelta
import random
from dateutil.relativedelta import relativedelta
import pytz
# Connect to MongoDB
client = pymongo.MongoClient("mongodb://root:password@localhost:27017/?authSource=admin")  # Replace with your actual MongoDB connection URI
# Set the time zone to GMT+7
local_tz = pytz.timezone('Asia/Bangkok')
# Function to insert data into the collection
def insert_data(collection, start_time, end_time, count):
    query = {"start_time": start_time}
    data = {
        "start_time": start_time,
        "end_time": end_time,
        "count": count
    }
    collection.update_one(query, {"$set": data}, upsert=True)


# Generate and insert random data for each collection
start_date = local_tz.localize(datetime(2020, 1, 1))
end_date = local_tz.localize(datetime(2024, 12, 31))

# Hourly data
hourly_collection = client["api_test"]["count_per_hour"]
current_time = start_date
while current_time <= end_date:
    count = random.randint(1, 100)
    insert_data(hourly_collection, current_time, current_time + timedelta(hours=1), count)
    current_time += timedelta(hours=1)

# Daily data
daily_collection = client["api_test"]["count_per_day"]
current_date = start_date
while current_date <= end_date:
    count = random.randint(100, 1000)
    insert_data(daily_collection, current_date, current_date + timedelta(days=1), count)
    current_date += timedelta(days=1)

# Monthly data
monthly_collection = client["api_test"]["count_per_month"]
current_month = start_date.replace(day=1)
while current_month <= end_date:
    count = random.randint(1000, 10000)
    insert_data(monthly_collection, current_month, current_month + relativedelta(months=1), count)
    current_month += relativedelta(months=1)

# Yearly data
yearly_collection = client["api_test"]["count_per_year"]
current_year = start_date.replace(month=1, day=1)
while current_year <= end_date:
    count = random.randint(10000, 100000)
    insert_data(yearly_collection, current_year, current_year + relativedelta(years=1), count)
    current_year += relativedelta(years=1)

print("Fake data inserted into MongoDB.")
