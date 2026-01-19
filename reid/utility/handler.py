from datetime import datetime, timedelta, timezone
import shortuuid
import time
import uuid


def get_datetime():
    return datetime.now()


def get_time():
    return int(time.time() * 1000)  # ms


def time2datetime(time):
    return datetime.fromtimestamp(time / 1000)


def datetime2time(dt: datetime):
    return dt.timestamp() * 1000


def get_fps(prev_time):
    new_time = get_time()
    fps = 1 / (new_time - prev_time) * 1000
    return int(fps), new_time


def get_id(short=False):
    if short is True:
        return shortuuid.uuid()
    return uuid.uuid4().hex


def split_time(start_time, end_time, batch_time):
    time_boxes = []

    current_time = start_time
    while current_time < end_time:
        next_time = current_time + batch_time
        if next_time > end_time:
            next_time = end_time

        time_boxes.append((current_time, next_time))
        current_time = next_time

    return time_boxes
