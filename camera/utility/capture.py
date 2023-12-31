from loguru import logger
import pickle
import redis
import time
import cv2

from utility.hparams import get_hparams_from_file, config_path
from utility.handler import get_time


def read_frame_with_count(source_id, source_uri):

    hps = get_hparams_from_file(config_path=config_path)

    redis_client = redis.Redis.from_url(hps.redis.uri)
    max_size = hps.redis.max_size
    batch_size = hps.redis.batch_size

    is_stream = is_stream_source(source_uri)

    cap = cv2.VideoCapture(source_uri)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) % 100
    logger.info("Load source: {}, resolution: {}, fps: {}, stream: {}".format(
        source_uri, (w, h), fps, is_stream
    ))

    n = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            time.sleep(hps.redis.time_retry)

            if not is_stream:
                logger.info("Not retry offline source: {}".format(source_uri))
            else:
                # retry stream only
                logger.info("Retry streaming source: {} in {} seconds".format(source_uri, hps.redis.time_retry))
                cap = cv2.VideoCapture(source_uri)
                ret, frame = cap.read()

            continue

        # count
        n += 1
        if n != batch_size:  # read every batch frame
            continue

        while True:
            if redis_client.llen(source_id) < max_size:
                # Add frame count to the frame
                frame_with_count = {'frame_time': get_time(), 'frame_data': frame}
                redis_client.rpush(source_id, pickle.dumps(frame_with_count))
                break

        n = 0
        time.sleep(0.001)  # wait time


def is_stream_source(source):
    if ('rtsp://' in source) or ('tcp://' in source):
        return True

    if ('http://' in source) or ('https://' in source):
        return True

    return False
