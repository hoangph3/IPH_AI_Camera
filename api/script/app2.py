from collections import defaultdict
from datetime import timedelta
from fastapi import Body, FastAPI, HTTPException, WebSocket
from pymongo import ASCENDING, MongoClient
from datetime import datetime, timedelta
from pydantic import BaseModel
import pytz
import uvicorn
from dateutil.relativedelta import relativedelta
from fastapi.middleware.cors import CORSMiddleware
import cv2

from fastapi import Response
from typing import Optional


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
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


class VisualizeRequest(BaseModel):
    range_type: str


# Connect to MongoDB
client = MongoClient("mongodb://admin:password@localhost:27017/?authSource=admin")
database_name = "iph"
# collection_name_day = "count_per_day"
# collection_name_month = "count_per_month"
collection_name_hour = "report_test"
db = client["iph"]
# Function to query data from MongoDB based on date range
print(db)

# def get_count_from_mongodb(start_time, end_time):
#     if (end_time - start_time).days > 30:
#         collection = client[database_name][collection_name_month]
#         collection_used = collection_name_month
#     elif (end_time - start_time).days > 1:
#         collection = client[database_name][collection_name_day]
#         collection_used = collection_name_day
#     else:
#         collection = client[database_name][collection_name_hour]
#         collection_used = collection_name_hour

#     query = {"start_time": {"$gte": start_time, "$lte": end_time}}
#     documents = collection.find(query)
#     count_sum = sum(doc.get("count", 0) for doc in documents)
#     return count_sum, collection_used


# Function to get the list of cameras from MongoDB


# def get_camera_list():
#     collection = client[database_name]["cam_list"]
#     # Exclude _id field from the result
#     cameras = collection.find({}, {"_id": 0})
#     return [Camera(**camera) for camera in cameras]


@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.post("/get_daily_data")
# async def get_daily_data(time):
#     try:
#         local_tz = pytz.timezone('Asis/Bangkok')
#     except Exception as e:
#         raise HTTPException(status_code=500,
#                             detail=str(e))


# @app.post("/count/")
# async def count_in_range(time_range: TimeRange):
#     try:
#         local_tz = pytz.timezone('Asia/Bangkok')
#         date_format = "%H:%M:%S %d/%m/%Y"
#         start_time = datetime.strptime(time_range.start_time, date_format)
#         end_time = datetime.strptime(time_range.end_time, date_format)
#         start_time = local_tz.localize(start_time)
#         end_time = local_tz.localize(end_time)

#         count, collection_used = get_count_from_mongodb(start_time, end_time)
#         return {"count": count, "collection_used": collection_used}
#     except Exception as e:
#         raise HTTPException(status_code=500,
#                             detail=str(e))

# Import the timedelta and relativedelta modules

# Modify the visualize_data endpoint


# @app.post("/visualize/")
# async def visualize_data(req_body: VisualizeRequest):
#     try:
#         current_time = datetime.now(pytz.timezone('Asia/Bangkok'))

#         if req_body.range_type == "day":
#             hours = list(range(0, 24))
#             collection = client[database_name][collection_name_hour]
#             end_time = current_time
#             start_time = current_time.replace(
#                 hour=0, minute=0, second=0, microsecond=0)
#             query = {"start_time": {"$gte": start_time, "$lte": end_time}}
#             count_list = [doc["count"] for doc in collection.find(query)]

#             first_index = hours.index(start_time.hour)
#             dynamic_hours = hours[first_index:]+hours[:first_index]
#             return {
#                 "date": dynamic_hours,
#                 "count_list": count_list,
#                 "collection_used": collection_name_hour}

#         elif req_body.range_type == "week":
#             days = list(range(1, 24))

#             collection = client[database_name][collection_name_day]
#             end_time = current_time.replace(
#                 hour=0, minute=0, second=0, microsecond=0)
#             start_time = end_time - timedelta(days=30)
#             query = {"start_time": {"$gte": start_time, "$lt": end_time}}
#             count_list = [doc["count"] for doc in collection.find(query)]

#             first_index = days.index(start_time.day)
#             dynamic_days = days[first_index:]+days[:first_index]
#             return {
#                 "date": dynamic_days,
#                 "count_list": count_list,
#                 "collection_used": collection_name_day}

#         elif req_body.range_type == "month":
#             months = list(range(1, 13))
#             collection = client[database_name][collection_name_month]
#             end_time = current_time.replace(
#                 day=1, hour=0, minute=0, second=0, microsecond=0)
#             start_time = end_time - relativedelta(months=12)
#             query = {"start_time": {"$gte": start_time, "$lt": end_time}}
#             count_list = [doc["count"] for doc in collection.find(query)]

#             first_index = months.index(start_time.month)
#             dynamic_months = months[first_index:]+months[:first_index]
#             return {
#                 "date": dynamic_months,
#                 "count_list": count_list,
#                 "collection_used": collection_name_month}

#         else:
#             raise HTTPException(
#                 status_code=400, detail="Invalid range type. Please provide 'hour', 'day', or 'month'.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Endpoint to get the list of cameras


# @app.get("/cameras/")
# async def get_cameras():
#     try:
#         cameras = get_camera_list()
#         return {"cameras": cameras}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/count_horizontal")
# async def get_data_api(time_range: TimeRange2):
#     try:
#         # Convert input strings to datetime objects
#         start_datetime = datetime.strptime(
#             time_range.start_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)
#         end_datetime = datetime.strptime(
#             time_range.end_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)

#         # MongoDB query to filter data based on start and end times
#         query = {
#             "start_time": {"$gte": start_datetime, "$lt": end_datetime}
#         }

#         # Fetch all data from the appropriate collection based on mode
#         collection_name = collection_name_hour if time_range.mode == "hour" else collection_name_day

#         data = list(db[collection_name].find(query))

#         # Extract start_time, end_time, days, and count from the documents
#         start_times = [(entry["start_time"] + timedelta(hours=7)
#                         ).strftime("%H:%M") for entry in data]
#         end_times = [(entry["end_time"] + timedelta(hours=7)
#                       ).strftime("%H:%M") for entry in data]
#         days = [(entry["start_time"] + timedelta(hours=7)
#                  ).strftime("%d-%m-%Y") for entry in data]
#         counts = [entry["count"] for entry in data]

#         return {"start_times": start_times, "end_times": end_times, "days": days, "counts": counts}
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
            time_range.start_time, "%H:%M %d/%m/%Y"
        ) - timedelta(hours=7)
        end_datetime = datetime.strptime(
            time_range.end_time, "%H:%M %d/%m/%Y"
        ) - timedelta(hours=7)
        print()
        # MongoDB query to filter data based on start and end times
        query = {"start_time": {"$gte": start_datetime, "$lt": end_datetime}}

        # Fetch all data from the "_test_test_test_test" collection
        data = list(db[collection_name_hour].find(query).sort("start_time", ASCENDING))

        # Extract start_time, end_time, days, and counts from the documents
        start_times = [
            (entry["start_time"] + timedelta(hours=7)).strftime("%H:%M")
            for entry in data
        ]
        end_times = [
            (entry["end_time"] + timedelta(hours=7)).strftime("%H:%M") for entry in data
        ]
        days = [
            (entry["start_time"] + timedelta(hours=7)).strftime("%d-%m-%Y")
            for entry in data
        ]

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
                day_key = (entry["start_time"] + timedelta(hours=7)).strftime(
                    "%d-%m-%Y"
                )
                count = (
                    entry["camera_counts"].get(camera_id, 0)
                    if camera_id
                    else entry["count"]
                )
                aggregated_counts[day_key] = aggregated_counts.get(day_key, 0) + count
                total_count_day += count

            # Extract aggregated data for response
            days = list(aggregated_counts.keys())
            counts = list(aggregated_counts.values())

        # Add total counts to the response
        return {
            "start_times": start_times,
            "end_times": end_times,
            "days": days,
            "counts": counts,
            "total_count_hour": total_count_hour,
            "total_count_day": total_count_day,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_time_range(req_body: VisualizeRequest):
    current_time_utc = datetime.utcnow()
    current_time_bangkok = current_time_utc + timedelta(hours=7)

    end_time_bangkok = current_time_bangkok

    if req_body.range_type == "day":
        start_time_bangkok = current_time_bangkok.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif req_body.range_type == "week":
        days_to_monday = current_time_bangkok.weekday()
        start_time_bangkok = current_time_bangkok - timedelta(days=days_to_monday)
        start_time_bangkok = start_time_bangkok.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    elif req_body.range_type == "month":
        start_time_bangkok = current_time_bangkok.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

    start_time_utc = start_time_bangkok - timedelta(hours=7)
    if req_body.range_type == "day":
        end_time_utc = end_time_bangkok - timedelta(hours=7) - timedelta(hours=1)
    elif req_body.range_type == "week":
        end_time_utc = end_time_bangkok - timedelta(hours=7) - timedelta(days=1)
    elif req_body.range_type == "month":
        end_time_utc = end_time_bangkok - timedelta(hours=7) - timedelta(days=1)

    return start_time_utc, end_time_utc


# async def get_mongo_query_and_collection(req_body: VisualizeRequest, start_time_utc, end_time_utc):
#     if req_body.range_type == "day":
#         collection = client[database_name][collection_name_hour]
#         query = {"start_time": {"$gte": start_time_utc, "$lte": end_time_utc}}
#     elif req_body.range_type == "week":
#         collection = client[database_name][collection_name_day]
#         query = {"start_time": {"$gte": start_time_utc, "$lt": end_time_utc}}
#     elif req_body.range_type == "month":
#         collection = client[database_name][collection_name_day]
#         query = {"start_time": {"$gte": start_time_utc, "$lt": end_time_utc}}

#     return collection, query
async def get_mongo_query_and_collection_v2(
    req_body: VisualizeRequest, start_time_utc, end_time_utc
):
    if req_body.range_type == "day" or req_body.range_type == "week":
        collection = client[database_name][collection_name_hour]
        query = {"start_time": {"$gte": start_time_utc, "$lt": end_time_utc}}
    elif req_body.range_type == "month":
        collection = client[database_name][collection_name_hour]
        query = {
            "start_time": {
                "$gte": start_time_utc,
                "$lt": end_time_utc + relativedelta(months=1),
            }
        }

    return collection, query


async def extract_and_return_response(
    documents, start_time_key, end_time_key, collection_name_used
):
    start_times = [
        (doc[start_time_key] + timedelta(hours=7)).strftime("%H:%M")
        for doc in documents
    ]
    end_times = [
        (doc[end_time_key] + timedelta(hours=7)).strftime("%H:%M") for doc in documents
    ]
    days = [
        (doc[start_time_key] + timedelta(hours=7)).strftime("%d-%m")
        for doc in documents
    ]  # Change format if needed
    counts = [doc["count"] for doc in documents]
    total_count = sum(counts)

    return {
        "start_times": start_times,
        "end_times": end_times,
        "days": days,
        "counts": counts,
        "collection_used": collection_name_used,
        "total_count": total_count,
    }


async def extract_and_return_response_v2(
    documents, start_time_key, end_time_key, collection_name_used, range_type
):
    if range_type == "week":
        # Calculate the start of the week
        current_time_bangkok = datetime.utcnow() + timedelta(hours=7)
        days_to_monday = current_time_bangkok.weekday()
        start_of_week_bangkok = current_time_bangkok - timedelta(days=days_to_monday)
        start_of_week_bangkok = start_of_week_bangkok.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Aggregate counts for each day of the week
        daily_counts = defaultdict(int)

        for doc in documents:
            day_of_week = (doc[start_time_key] + timedelta(hours=7)).strftime(
                "%d-%m %a"
            )
            daily_counts[day_of_week] += doc["count"]

        # Filter only days from the start of the week until the day before the current day
        filtered_counts = {
            key: value
            for key, value in daily_counts.items()
            if key <= current_time_bangkok.strftime("%d-%m %a")
        }

        # Format aggregated data
        start_times = list(filtered_counts.keys())
        end_times = (
            start_times
        )  # Since it's aggregated for each day, end time is the same as start time
        days = [
            start_time.split()[0] for start_time in start_times
        ]  # Extracting only the date
        counts = list(filtered_counts.values())
        total_count = sum(counts)
    elif range_type == "month":
        # Calculate the start of the month
        current_time_bangkok = datetime.utcnow() + timedelta(hours=7)
        start_of_month_bangkok = current_time_bangkok.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        # Aggregate counts for each day of the month
        daily_counts = defaultdict(int)

        for doc in documents:
            day_of_month = (doc[start_time_key] + timedelta(hours=7)).strftime("%d-%m")
            daily_counts[day_of_month] += doc["count"]

        # Filter only days from the start of the month until the day before the current day
        filtered_counts = {
            key: value
            for key, value in daily_counts.items()
            if key <= current_time_bangkok.strftime("%d-%m")
        }

        # Format aggregated data
        start_times = list(filtered_counts.keys())
        end_times = [
            (
                start_of_month_bangkok + timedelta(days=int(key.split("-")[0]) - 1)
            ).strftime("%d-%m")
            for key in filtered_counts.keys()
        ]  # Calculate end times based on day of the month
        days = start_times  # Use start times as days
        counts = list(filtered_counts.values())
        total_count = sum(counts)
    else:
        # Default format for other range types
        start_times = [
            (doc[start_time_key] + timedelta(hours=7)).strftime("%H:%M")
            for doc in documents
        ]
        end_times = [
            (doc[end_time_key] + timedelta(hours=7)).strftime("%H:%M")
            for doc in documents
        ]
        days = [
            (doc[start_time_key] + timedelta(hours=7)).strftime("%d-%m")
            for doc in documents
        ]
        counts = [doc["count"] for doc in documents]
        total_count = sum(counts)

    return {
        "start_times": start_times,
        "end_times": end_times,
        "days": days,
        "counts": counts,
        "collection_used": collection_name_used,
        "total_count": total_count,
    }


@app.post("/visualize_v2/")
async def visualize_data(req_body: VisualizeRequest):
    try:
        start_time_utc, end_time_utc = await get_time_range(req_body)
        print(start_time_utc, end_time_utc)

        collection, query = await get_mongo_query_and_collection_v2(
            req_body, start_time_utc, end_time_utc
        )

        # Retrieve documents in the specified period
        documents = list(collection.find(query))

        if req_body.range_type == "day":
            return await extract_and_return_response_v2(
                documents,
                "start_time",
                "end_time",
                collection_name_hour,
                req_body.range_type,
            )
        elif req_body.range_type == "week":
            return await extract_and_return_response_v2(
                documents,
                "start_time",
                "end_time",
                collection_name_hour,
                req_body.range_type,
            )
        elif req_body.range_type == "month":
            return await extract_and_return_response_v2(
                documents,
                "start_time",
                "end_time",
                collection_name_hour,
                req_body.range_type,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid range type. Please provide 'day', 'week', or 'month'.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def query_mongo(start_time, end_time, start_date, end_date):
    results = {"start_times": [], "end_times": [], "days": [], "counts": []}

    # Convert input date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%d/%m/%Y")
    end_datetime = datetime.strptime(end_date, "%d/%m/%Y")

    # Iterate over the date range
    current_date = start_datetime
    while current_date <= end_datetime:
        # Build query for each day
        query = {
            "start_time": {
                "$gte": current_date.replace(
                    hour=int(start_time.split(":")[0]),
                    minute=int(start_time.split(":")[1]),
                )
            },
            "end_time": {
                "$lte": current_date.replace(
                    hour=int(end_time.split(":")[0]), minute=int(end_time.split(":")[1])
                )
            },
        }

        # Execute query and sum counts
        day_results = db[collection_name_hour].find(
            query, {"start_time": 1, "end_time": 1, "count": 1}
        )
        total_count = sum(result["count"] for result in day_results)

        # Append results
        results["start_times"].append(
            current_date.replace(
                hour=int(start_time.split(":")[0]), minute=int(start_time.split(":")[1])
            ).strftime("%H:%M")
        )
        results["end_times"].append(
            current_date.replace(
                hour=int(end_time.split(":")[0]), minute=int(end_time.split(":")[1])
            ).strftime("%H:%M")
        )
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

    result = query_mongo(start_time, end_time, start_date, end_date)
    return {"results": result}


def gen_frames():  # generate frame by frame from camera
    camera = cv2.VideoCapture("rtsp://kotora:ktr123@192.168.1.182:554/stream1")
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )  # concat frame one by one and show result


@app.get("/video_feed")
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


def query_mongo_for_camera(start_time, end_time, start_date, end_date, camera_id):
    results = {"start_times": [], "end_times": [], "days": [], "counts": []}

    # Convert input date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%d/%m/%Y")
    end_datetime = datetime.strptime(end_date, "%d/%m/%Y")

    # Iterate over the date range
    current_date = start_datetime
    while current_date <= end_datetime:
        # Build query for each day and the specified camera
        query = {
            "start_time": {
                "$gte": current_date.replace(
                    hour=int(start_time.split(":")[0]),
                    minute=int(start_time.split(":")[1]),
                )
            },
            "end_time": {
                "$lte": current_date.replace(
                    hour=int(end_time.split(":")[0]), minute=int(end_time.split(":")[1])
                )
            },
            "camera_counts." + camera_id: {"$exists": True},
        }

        # Execute query and get counts for the specified camera
        day_results = db[collection_name_hour].find(
            query, {"start_time": 1, "end_time": 1, f"camera_counts.{camera_id}": 1}
        )
        counts_for_camera = [
            result["camera_counts"][camera_id] for result in day_results
        ]

        # Append results
        results["start_times"].append(
            current_date.replace(
                hour=int(start_time.split(":")[0]), minute=int(start_time.split(":")[1])
            ).strftime("%H:%M")
        )
        results["end_times"].append(
            current_date.replace(
                hour=int(end_time.split(":")[0]), minute=int(end_time.split(":")[1])
            ).strftime("%H:%M")
        )
        results["days"].append(current_date.strftime("%d/%m/%Y"))
        results["counts"].append(sum(counts_for_camera))

        # Move to the next day
        current_date += timedelta(days=1)

    return results


# Updated endpoint for counts for a specific camera


@app.post("/count_vertical_camera")
async def get_counts_for_camera(request_data: dict):
    try:
        time_params = request_data.get("time_params", {})
        camera_id = request_data.get("camera_id")

        if not camera_id:
            raise HTTPException(
                status_code=400,
                detail="The 'camera_id' field is required in the request body.",
            )

        results = query_mongo_for_camera(
            time_params.get("start_time"),
            time_params.get("end_time"),
            time_params.get("start_date"),
            time_params.get("end_date"),
            camera_id,
        )

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# # Define a new Pydantic model for the request body
# class CountForSpecificCameraRequest(BaseModel):
#     camera_id: str
#     start_time: str
#     end_time: str
#     mode: str  # Include mode in the model

# New function to retrieve count data for a specific camera_id


# def get_count_for_specific_camera(start_time, end_time, camera_id, mode):
#     # Convert input strings to datetime objects
#     start_datetime = datetime.strptime(
#         start_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)
#     end_datetime = datetime.strptime(
#         end_time, "%H:%M %d/%m/%Y") - timedelta(hours=7)

#     # MongoDB query to filter data based on start and end times for the specified camera_id
#     query = {
#         "start_time": {"$gte": start_datetime, "$lt": end_datetime},
#         f"camera_counts.{camera_id}": {"$exists": True}
#     }

#     # Fetch all data from the appropriate collection based on mode
#     collection_name = collection_name_hour if mode == "hour" else collection_name_day

#     # Retrieve documents based on the query
#     data = list(db[collection_name].find(query))

#     # Extract start_time, end_time, days, and count from the documents
#     start_times = [(entry["start_time"] + timedelta(hours=7)
#                     ).strftime("%H:%M") for entry in data]
#     end_times = [(entry["end_time"] + timedelta(hours=7)
#                   ).strftime("%H:%M") for entry in data]
#     days = [(entry["start_time"] + timedelta(hours=7)).strftime("%d-%m-%Y")
#             for entry in data]
#     counts = [entry["camera_counts"][camera_id] for entry in data]

#     return {"start_times": start_times, "end_times": end_times, "days": days, "counts": counts}

# New API endpoint to retrieve count data for a specific camera_id


# @app.post("/count_horizontal_camera")
# async def count_for_specific_camera(request_data: CountForSpecificCameraRequest):
#     try:
#         result = get_count_for_specific_camera(
#             request_data.start_time, request_data.end_time, request_data.camera_id, request_data.mode)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
