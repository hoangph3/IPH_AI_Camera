from collections import defaultdict
from datetime import timedelta
from fastapi import Body, FastAPI, HTTPException, WebSocket
from pymongo import ASCENDING, MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import uvicorn
from dateutil.relativedelta import relativedelta
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Tuple
from typing import Optional
from pytz import timezone
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)
# Pydantic model for camera data
class CountHorizontalRequest(BaseModel):
    start_time: str
    end_time: str
    mode: str
    camera_id: Optional[str] = None

class Camera(BaseModel):
    name: str
    rtsp_url: str


class TimeRange(BaseModel):
    start_time: str
    end_time: str


class TimeRange2(BaseModel):
    start_time: str
    end_time: str
    mode: str  # Include mode in the model
class RangeType(BaseModel):
    range_type: str


# class VisualizeRequest(BaseModel):
#     range_type: str


# Connect to MongoDB
client = MongoClient(
    "mongodb://admin:password@localhost:27017/admin")
database_name = "iph"
collection_name_hour = "report"
db = client[database_name]
# Correct timezone string for GMT+7
local_timezone = timezone('Asia/Bangkok')


def query_mongo_for_camera(start_time, end_time, start_date, end_date, camera_id):
    results = {
        "start_times": [],
        "end_times": [],
        "days": [],
        "counts": []
    }

    # Convert input date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%d/%m/%Y")
    end_datetime = datetime.strptime(end_date, "%d/%m/%Y")

    # Iterate over the date range
    current_date = start_datetime
    while current_date <= end_datetime:
        # Build query for each day and the specified camera
        query = {
            "start_time": {
                "$gte": current_date.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]))
            },
            "end_time": {
                "$lte": current_date.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]))
            },
            "camera_counts." + camera_id: {"$exists": True}
        }

        # Execute query and get counts for the specified camera
        day_results = db[collection_name_hour].find(
            query, {"start_time": 1, "end_time": 1, f"camera_counts.{camera_id}": 1})
        counts_for_camera = [result["camera_counts"][camera_id]
                             for result in day_results]

        # Append results
        results["start_times"].append(current_date.replace(hour=int(start_time.split(
            ':')[0]), minute=int(start_time.split(':')[1])).strftime("%H:%M"))
        results["end_times"].append(current_date.replace(hour=int(
            end_time.split(':')[0]), minute=int(end_time.split(':')[1])).strftime("%H:%M"))
        results["days"].append(current_date.strftime("%d/%m/%Y"))
        results["counts"].append(sum(counts_for_camera))

        # Move to the next day
        current_date += timedelta(days=1)

    return results
# Updated endpoint for counts for a specific camera


@app.post("/count_vertical_camera")
async def get_counts_for_camera(
    request_data: dict
):
    try:
        time_params = request_data.get("time_params", {})
        camera_id = request_data.get("camera_id")

        if not camera_id:
            raise HTTPException(
                status_code=400, detail="The 'camera_id' field is required in the request body.")

        results = query_mongo_for_camera(
            time_params.get("start_time"),
            time_params.get("end_time"),
            time_params.get("start_date"),
            time_params.get("end_date"),
            camera_id
        )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def query_mongo(start_time, end_time, start_date, end_date):
    results = {
        "start_times": [],
        "end_times": [],
        "days": [],
        "counts": []
    }

    # Convert input date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%d/%m/%Y")
    end_datetime = datetime.strptime(end_date, "%d/%m/%Y")

    # Iterate over the date range
    current_date = start_datetime
    while current_date <= end_datetime:
        # Build query for each day
        query = {
            "start_time": {"$gte": current_date.replace(hour=int(start_time.split(':')[0]), minute=int(start_time.split(':')[1]))},
            "end_time": {"$lte": current_date.replace(hour=int(end_time.split(':')[0]), minute=int(end_time.split(':')[1]))}
        }
        print(query)
        # Execute query and sum counts
        day_results = db[collection_name_hour].find(
            query, {"start_time": 1, "end_time": 1, "count": 1})
        total_count = sum(result["count"] for result in day_results)

        # Append results
        results["start_times"].append(current_date.replace(hour=int(start_time.split(
            ':')[0]), minute=int(start_time.split(':')[1])).strftime("%H:%M"))
        results["end_times"].append(current_date.replace(hour=int(
            end_time.split(':')[0]), minute=int(end_time.split(':')[1])).strftime("%H:%M"))
        results["days"].append(current_date.strftime("%d/%m/%Y"))
        results["counts"].append(total_count)

        # Move to the next day
        current_date += timedelta(days=1)

    return results


@app.post("/count_vertical")
def get_counts(query_params: dict):
    start_time = query_params["start_time"]
    end_time = query_params["end_time"]
    start_date = query_params["start_date"]
    end_date = query_params["end_date"]
    print(start_date)
    result = query_mongo(start_time, end_time, start_date, end_date)
    return {"results": result}



@app.post("/visualize_v2")
async def get_counts(range_type: RangeType = Body(...)):
    # Validate range_type
    valid_range_types = ['day', 'week', 'month']
    if range_type.range_type not in valid_range_types:
        raise HTTPException(status_code=400, detail="Invalid range_type. Choose from 'day', 'week', or 'month'.")

    # Get current date in server's timezone (GMT+7)
    current_date_gmt7 = datetime.now(local_timezone)

    # Define start and end time based on range_type
    if range_type.range_type == 'day':
        start_time = datetime(current_date_gmt7.year, current_date_gmt7.month, current_date_gmt7.day, 0, 0, 0) - timedelta(hours=7)
        end_time = datetime(current_date_gmt7.year, current_date_gmt7.month, current_date_gmt7.day, current_date_gmt7.hour, 0, 0) - timedelta(hours=7)
    elif range_type.range_type == 'week':
        start_time = current_date_gmt7 - timedelta(days=current_date_gmt7.weekday())
       
        end_time = current_date_gmt7.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
    elif range_type.range_type == 'month':
        # Set the start_time to the first day of the month
        start_time = datetime(current_date_gmt7.year, current_date_gmt7.month, 1, 0, 0, 0) - timedelta(hours=7)

        # Set the end_time to the day before the current day
        end_time = datetime(current_date_gmt7.year, current_date_gmt7.month, current_date_gmt7.day, 0, 0, 0) - timedelta(hours=7)

    # Query MongoDB, 
    results = db[collection_name_hour].find({
        'start_time': {'$gte': start_time, '$lt': end_time}
    })

    # Process results and prepare response
    if range_type.range_type == 'day':
        start_times, end_times, counts, days = [], [], [], []
        total_count = 0

        for result in results:
            # Convert UTC time from MongoDB to local time (GMT+7)
            start_time_local = result['start_time'].astimezone(local_timezone) + timedelta(hours=7)
            end_time_local = result['end_time'].astimezone(local_timezone) + timedelta(hours=7)

            start_times.append(start_time_local.strftime('%H:%M'))
            end_times.append(end_time_local.strftime('%H:%M'))
            counts.append(result['count'])
            total_count += result['count']
            # Include only the DD-MM format in the "days" field without the time part
            days.append(start_time_local.strftime('%d-%m'))

        response = {
            'start_times': start_times,
            'end_times': end_times,
            'days': days,
            'counts': counts,
            'collection_used': 'report_test',
            'total_count': total_count
        }

    elif range_type.range_type == 'week':
    # Calculate the start of the week (Monday) and the end of the previous day
        start_of_week = current_date_gmt7 - timedelta(days=current_date_gmt7.weekday())
        end_of_previous_day = current_date_gmt7.replace(hour=0, minute=0, second=0, microsecond=0) -timedelta(seconds=1)
        
        # Query MongoDB for counts for each day within the week
        results = db[collection_name_hour].aggregate([
            {
                '$match': {
                    'start_time': {'$gte': start_of_week, '$lt': end_of_previous_day}
                }
            },
            {
                '$project': {
                    'day_of_month': {'$dayOfMonth': '$start_time'},
                    'count': '$count'
                }
            },
            {
                '$group': {
                    '_id': '$day_of_month',
                    'count': {'$sum': '$count'}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ])

        # Process results and prepare response
        days, counts = [], []
        total_count = 0

        for result in results:
            print(result)
            day_of_month = result['_id']
            days.append(day_of_month)
            counts.append(result['count'])
            total_count += result['count']

        response = {
            'days': days,
            'counts': counts,
            'collection_used': 'report_test',
            'total_count': total_count
        }
    elif range_type.range_type == 'month':
        # Set the start_time to the first day of the month
        start_time = datetime(current_date_gmt7.year, current_date_gmt7.month, 1, 0, 0, 0)
        print(start_time)
        # Set the end_time to the day before the current day
        end_time = datetime(current_date_gmt7.year, current_date_gmt7.month, current_date_gmt7.day, 0, 0, 0) - timedelta(seconds=1)
        print(end_time)

        # Query MongoDB using aggregation
        results = db[collection_name_hour].aggregate([
            {
                '$match': {
                    'start_time': {'$gte': start_time, '$lt': end_time}
                }
            },
            {
                '$project': {
                    'day_of_month': {'$dayOfMonth': '$start_time'},
                    'count': '$count'
                }
            },
            {
                '$group': {
                    '_id': '$day_of_month',
                    'count': {'$sum': '$count'}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ])

        # Process results and prepare response
        days, counts = [], []
        total_count = 0

        for result in results:
            day_of_month = result['_id']
            # Format the day as "dd-mm"
            formatted_day = start_time.replace(day=day_of_month).strftime('%d-%m')
            days.append(formatted_day)
            counts.append(result['count'])
            total_count += result['count']

        response = {
            'days': days,
            'counts': counts,
            'collection_used': 'report_test',
            'total_count': total_count
        }

    return response
# @app.post("/count_horizontal_v2")
# async def get_data_api(time_range: CountHorizontalRequest):
#     try:
#         # Extract camera_id from the request
#         camera_id = time_range.camera_id

#         # Convert input strings to datetime objects
#         start_datetime = datetime.strptime(time_range.start_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)
#         end_datetime = datetime.strptime(time_range.end_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)

#         # Generate time entries for the entire range
#         time_entries = [(start_datetime + timedelta(hours=i)).strftime("%H:%M") for i in range(int((end_datetime - start_datetime).total_seconds() / 3600) + 1)]

#         # MongoDB query to filter data based on start and end times
#         query = {
#             "start_time": {"$gte": start_datetime, "$lt": end_datetime}
#         }

#         # Fetch all data from the "report_test" collection
#         collection_name = "report_test"
#         data = list(db[collection_name].find(query))

#         # Initialize counts and total_count
#         counts = []
#         days= []
#         total_count = 0

#         # Iterate over time entries and handle camera_id logic
#         for entry in data:
#             if camera_id:
#                 count = entry["camera_counts"].get(camera_id, 0)
#                 counts.append(count)
#                 total_count += count
#             else:
#                 count = entry["count"]
                
#                 counts.append(count)
#                 total_count += count

#         # Calculate total count for "hour" mode
#         total_count_hour = sum(counts) if time_range.mode == "hour" else 0

#         # Initialize total_count_day for "day" mode
#         total_count_day = sum(counts) if time_range.mode == "day" else 0

#         # If mode is "day," aggregate counts for each day
#         if time_range.mode == "day":
#             # Aggregate counts for each day
#             aggregated_counts = {}
#             for entry in data:
#                 day_key = entry["start_time"].strftime("%d-%m-%Y")
#                 count = entry["camera_counts"].get(camera_id, 0) if camera_id else entry["count"]
#                 aggregated_counts[day_key] = aggregated_counts.get(day_key, 0) + count
#                 total_count_day += count

#             # Extract aggregated data for response
#             days = list(aggregated_counts.keys())
#             counts = list(aggregated_counts.values())
            
#         # Add total counts to the response
#         return {
#             "start_times": time_entries,
#             "end_times": time_entries,
#             "days": days if time_range.mode == "day" else [],
#             "counts": counts if time_range.mode == "day" else counts,
#             "total_count_hour": total_count_hour,
#             "total_count_day": total_count_day
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/count_horizontal_v2")
async def get_data_api(time_range: CountHorizontalRequest):
    try:
        # Extract camera_id from the request
        camera_id = time_range.camera_id

        print(f"Received time_range from Postman: {time_range}")
        print(f"Received camera_id from Postman: {camera_id}")

        # Convert input strings to datetime objects
        start_datetime = datetime.strptime(
            time_range.start_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)
        end_datetime = datetime.strptime(
            time_range.end_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)
        print()
        # MongoDB query to filter data based on start and end times
        query = {
            "start_time": {"$gte": start_datetime, "$lt": end_datetime}
        }

        # Fetch all data from the "_test_test_test_test" collection
        data = list(db[collection_name_hour].find(query).sort("start_time", ASCENDING))

        # Extract start_time, end_time, days, and counts from the documents
        start_times = [(entry["start_time"] + timedelta(hours=7)
                        ).strftime("%H:%M") for entry in data]
        end_times = [(entry["end_time"] + timedelta(hours=7)
                      ).strftime("%H:%M") for entry in data]
        days = [(entry["start_time"] + timedelta(hours=7)
                 ).strftime("%d-%m-%Y") for entry in data]

        # Initialize counts and total_count
        counts = []
        total_count = 0

        # Iterate over data and handle camera_id logic
        for entry in data:
            if camera_id:
                count = entry["camera_counts"].get(camera_id, 0)
                counts.append(count)
                total_count += count
            else:
                count = entry["count"]
                counts.append(count)
                total_count += count

        # Calculate total count for "hour" mode
        total_count_hour = sum(counts) if time_range.mode == "hour" else 0

        # Initialize total_count_day for "day" mode
        total_count_day = 0

        # If mode is "day," aggregate counts for each day
        if time_range.mode == "day":
            # Aggregate counts for each day
            aggregated_counts = {}
            for entry in data:
                day_key = (entry["start_time"] + timedelta(hours=7)).strftime("%d-%m-%Y")
                count = entry["camera_counts"].get(camera_id, 0) if camera_id else entry["count"]
                aggregated_counts[day_key] = aggregated_counts.get(day_key, 0) + count
                total_count_day += count

            # Extract aggregated data for response
            days = list(aggregated_counts.keys())
            counts = list(aggregated_counts.values())

        # Add total counts to the response
        return {"start_times": start_times, "end_times": end_times, "days": days, "counts": counts,
                "total_count_hour": total_count_hour, "total_count_day": total_count_day}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)