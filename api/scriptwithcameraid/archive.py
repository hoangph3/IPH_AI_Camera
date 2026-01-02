    # elif range_type.range_type == 'week':
    # # Calculate the start of the week (Monday) and the end of the previous day
    #     start_of_week = current_date_gmt7 - timedelta(days=current_date_gmt7.weekday())
    #     end_of_previous_day = current_date_gmt7.replace(hour=0, minute=0, second=0, microsecond=0) -timedelta(seconds=1)
        
    #     # Query MongoDB for counts for each day within the week
    #     results = db[collection_name_hour].aggregate([
    #         {
    #             '$match': {
    #                 'start_time': {'$gte': start_of_week, '$lt': end_of_previous_day}
    #             }
    #         },
    #         {
    #             '$project': {
    #                 'day_of_month': {'$dayOfMonth': '$start_time'},
    #                 'count': '$count'
    #             }
    #         },
    #         {
    #             '$group': {
    #                 '_id': '$day_of_month',
    #                 'count': {'$sum': '$count'}
    #             }
    #         },
    #         {
    #             '$sort': {'_id': 1}
    #         }
    #     ])

    #     # Process results and prepare response
    #     days, counts = [], []
    #     total_count = 0

    #     for result in results:
    #         print(result)
    #         day_of_month = result['_id']
    #         days.append(day_of_month)
    #         counts.append(result['count'])
    #         total_count += result['count']

    #     response = {
    #         'days': days,
    #         'counts': counts,
    #         'collection_used': collection_name_hour,
    #         'total_count': total_count
    #     }
    
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

# elif range_type.range_type == 'month':
    #     # Set the start_time to the first day of the month
    #     start_time = datetime(current_date_gmt7.year, current_date_gmt7.month, 1, 0, 0, 0)
    #     print(start_time)
    #     # Set the end_time to the day before the current day
    #     end_time = datetime(current_date_gmt7.year, current_date_gmt7.month, current_date_gmt7.day, 0, 0, 0) - timedelta(seconds=1)
    #     print(end_time)

    #     # Query MongoDB using aggregation
    #     results = db[collection_name_hour].aggregate([
    #         {
    #             '$match': {
    #                 'start_time': {'$gte': start_time, '$lt': end_time}
    #             }
    #         },
    #         {
    #             '$project': {
    #                 'day_of_month': {'$dayOfMonth': '$start_time'},
    #                 'count': '$count'
    #             }
    #         },
    #         {
    #             '$group': {
    #                 '_id': '$day_of_month',
    #                 'count': {'$sum': '$count'}
    #             }
    #         },
    #         {
    #             '$sort': {'_id': 1}
    #         }
    #     ])

    #     # Process results and prepare response
    #     days, counts = [], []
    #     total_count = 0

    #     for result in results:
    #         day_of_month = result['_id']
    #         # Format the day as "dd-mm"
    #         formatted_day = start_time.replace(day=day_of_month).strftime('%d-%m')
    #         days.append(formatted_day)
    #         counts.append(result['count'])
    #         total_count += result['count']

    #     response = {
    #         'days': days,
    #         'counts': counts,
    #         'collection_used': collection_name_hour,
    #         'total_count': total_count
    #     }