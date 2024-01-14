from collections import defaultdict
from datetime import timedelta
from fastapi import Body, FastAPI, HTTPException, WebSocket
from pymongo import ASCENDING, MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel

import uvicorn
from dateutil.relativedelta import relativedelta
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Tuple
from typing import Optional
from pytz import timezone
import calendar

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
client = MongoClient("mongodb://admin:password@localhost:27017/admin")
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
    # print(start_datetime)
    # print(end_datetime)

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
        day_results = list(db[collection_name_hour].find(query))
        print(day_results)

        total_count = 0
        if len(day_results) > 0:
            for res in day_results:
                total_count += res['count']

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

@app.post("/count_vertical_v2")
def get_counts(query_params: dict):
    results = []
    start_time = query_params["start_time"]
    end_time = query_params["end_time"]
    start_date = query_params["start_date"]
    end_date = query_params["end_date"]

    start = int(start_time.split(":")[0])
    end = int(end_time.split(":")[0])

    # print(start_date)
    starts = [f'{i}:00' for i in range(start,end)]
    ends = [f'{i}:00' for i in range(start+1,end+1)]

    for x1,x2 in zip(starts,ends):
        results.append(query_mongo(x1,x2,start_date,end_date))
    # result = query_mongo(start_time, end_time, start_date, end_date)
    return {"starts": starts,
            "ends": ends,
            "results": results}


@app.post("/visualize_v2")
async def get_counts(range_type: RangeType = Body(...)):
    # Validate range_type
    valid_range_types = ['day', 'week', 'month']
    if range_type.range_type not in valid_range_types:
        raise HTTPException(status_code=400, detail="Invalid range_type. Choose from 'day', 'week', or 'month'.")

    # Get current date in server's timezone (GMT+7)
    current_date = datetime.now()
    print(current_date)

    # Define start and end time based on range_type
    if range_type.range_type == 'day':
        start_time = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0) 

        end_time = datetime(current_date.year, current_date.month, current_date.day, current_date.hour, 0, 0) 

    elif range_type.range_type == 'week':
        
        start_time = current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=current_date.weekday())
        print(start_time)
        end_time = current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        print(end_time)
        
    elif range_type.range_type == 'month':    
        # Set the start_time to the first day of the month
        start_time = datetime(current_date.year, current_date.month, 1, 0, 0, 0) 

        # Set the end_time to the day before the current day
        end_time = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0) 

    # Query MongoDB, 
    
    results = list(db[collection_name_hour].find({
        'start_time': {'$gte': start_time, '$lt': end_time}
    }))
    print(results)
    
    

    # Process results and prepare response
    if range_type.range_type == 'day':
        start_times, end_times, counts, days = [], [], [], []
        total_count = 0

        for result in results:
            print(result['start_time'])
            # Convert UTC time from MongoDB to local time (GMT+7)
            start_time_local = result['start_time'].astimezone(local_timezone) 
            end_time_local = result['end_time'].astimezone(local_timezone) 

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
            'collection_used': collection_name_hour,
            'total_count': total_count
        }
    elif range_type.range_type == 'week':
        # Initialize a dictionary to store counts for each day
        day_counts = {}

        total_count = 0

        start_time = current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=current_date.weekday())
        print(start_time)
        end_time = current_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        print(end_time)

    
        # Process results and sum counts for each day
        for result in results:
            # Adjust the date formatting to match the format in MongoDB documents
            day_key = result['start_time'].strftime('%d-%m')
            day_counts[day_key] = day_counts.get(day_key, 0) + result['count']
            total_count += result['count']

        # Prepare response
        response = {
            'days': list(day_counts.keys()),  # List of days in 'dd-mm' format
            'counts': list(day_counts.values()),  # List of counts for each day
            'total_count': total_count
        }

    elif range_type.range_type == 'month':
        # Determine the number of days in the current month
        _, last_day_of_month = calendar.monthrange(current_date.year, current_date.month)

        # Initialize a dictionary to store counts for each day of the month
        day_counts = {day: 0 for day in range(1, last_day_of_month + 1)}

        total_count = 0

        # Find the first day of the month
        start_of_month = datetime(current_date.year, current_date.month, 1, 0, 0, 0)

        for result in results:
            # Convert UTC time from MongoDB to local time (GMT+7)
            start_time_local = result['start_time']

            # Calculate the day difference from the start of the month
            days_since_start_of_month = (start_time_local - start_of_month).days

            # Check if the day is within the desired range (until the last day of the month)
            if 0 <= days_since_start_of_month < last_day_of_month:
                # Add the count to the corresponding day of the month
                day_counts[start_time_local.day] += result['count']
                total_count += result['count']

        # Prepare response
        response = {
            'days': list(day_counts.keys()),  # List of days (1-last_day_of_month)
            'counts': list(day_counts.values()),  # List of counts for each day
            'collection_used': collection_name_hour,
            'total_count': total_count
        }
    return response

# @app.post("/count_horizontal_v2")
# async def get_data_api(time_range: CountHorizontalRequest):
#     try:
#         # Extract camera_id from the request
#         camera_id = time_range.camera_id

#         print(f"Received time_range from Postman: {time_range}")
#         print(f"Received camera_id from Postman: {camera_id}")

#         # Convert input strings to datetime objects
#         start_datetime = datetime.strptime(
#             time_range.start_time, "%H:%M %d/%m/%Y") 
#         end_datetime = datetime.strptime(
#             time_range.end_time, "%H:%M %d/%m/%Y") 
        
#         # MongoDB query to filter data based on start and end times
#         query = {
#             "start_time": {"$gte": start_datetime, "$lt": end_datetime}
#         }

#         # Fetch all data from the "_test_test_test_test" collection
#         data = list(db[collection_name_hour].find(query).sort("start_time", ASCENDING))
        
#         # Extract start_time, end_time, days, and counts from the documents
#         start_times = [(entry["start_time"]
#                         ).strftime("%H:%M") for entry in data]
#         end_times = [(entry["end_time"]
#                       ).strftime("%H:%M") for entry in data]
#         days = [(entry["start_time"]
#                  ).strftime("%d-%m-%Y") for entry in data]

#         # Initialize counts and total_count
#         counts = []
#         total_count = 0

#         # Iterate over data and handle camera_id logic
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
#         total_count_day = 0

#         # If mode is "day," aggregate counts for each day
#         if time_range.mode == "day":
#             # Aggregate counts for each day
#             aggregated_counts = {}
#             for entry in data:
#                 day_key = (entry["start_time"] + timedelta(hours=7)).strftime("%d-%m-%Y")
#                 count = entry["camera_counts"].get(camera_id, 0) if camera_id else entry["count"]
#                 aggregated_counts[day_key] = aggregated_counts.get(day_key, 0) + count
#                 total_count_day += count
            
#             # Extract aggregated data for response
#             days = list(aggregated_counts.keys())
#             counts = list(aggregated_counts.values())

#         # Add total counts to the response
#         return {"start_times": start_times, "end_times": end_times, "days": days, "counts": counts,
#                 "total_count_hour": total_count_hour, "total_count_day": total_count_day}
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
            time_range.start_time, "%H:%M %d/%m/%Y") 
        end_datetime = datetime.strptime(
            time_range.end_time, "%H:%M %d/%m/%Y") 
        print()
        # MongoDB query to filter data based on start and end times
        query = {
            "start_time": {"$gte": start_datetime, "$lt": end_datetime}
        }

        # Fetch all data from the "_test_test_test_test" collection
        data = list(db[collection_name_hour].find(query).sort("start_time", ASCENDING))

        # Extract start_time, end_time, days, and counts from the documents
        start_times = [(entry["start_time"] 
                        ).strftime("%H:%M") for entry in data]
        end_times = [(entry["end_time"] 
                      ).strftime("%H:%M") for entry in data]
        days = [(entry["start_time"]
                 ).strftime("%d-%m-%Y") for entry in data]
        print(days)
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
                day_key = (entry["start_time"]).strftime("%d-%m-%Y")
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
    uvicorn.run("app:app", host="0.0.0.0", port=5000,reload=True )