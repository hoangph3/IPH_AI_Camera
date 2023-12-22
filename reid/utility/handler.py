import time


def get_time():
    return int(time.time() * 1000)  # ms


def get_fps(prev_time):
    new_time = get_time()
    fps = 1 / (new_time - prev_time) * 1000
    return int(fps), new_time
