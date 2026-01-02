from pathlib import Path
from loguru import logger
import pickle
import redis
import time
import cv2
import re


from utility.hparams import get_hparams_from_file, config_path
from utility.handler import get_time

# Define the camera ID to IP address mapping
CAMERA_IP_MAPPING = {
    "Cam1": "10.0.0.201",
    "Cam2": "10.0.0.202",
    "Cam3": "10.0.0.203",
    "Cam4": "10.0.0.204",
    "Cam5": "10.0.0.205",
    "Cam6": "10.0.0.206",
    "Cam7": "10.0.0.207",
    "Cam8": "10.0.0.208",
    "Cam9": "10.0.0.209",
    "Cam10": "10.0.0.210",
    "Cam11": "10.0.0.211",
    "Cam12": "10.0.0.212",
    "Cam13": "10.0.0.213",
    "Cam14": "10.0.0.214",
    "Cam15": "10.0.0.215",
    "Cam16": "10.0.0.216",
    "Cam17": "10.0.0.217",
    "Cam18": "10.0.0.218",
    "Cam19": "10.0.0.219",
    "Cam20": "10.0.0.220",
    "Cam21": "10.0.0.221",
    "Cam22": "192.168.0.149",
    "Cam23": "192.168.0.168",
    "Cam23": "192.168.0.251"
}
def read_frame_with_count(source):
    hps = get_hparams_from_file(config_path=config_path)

    redis_client = redis.Redis.from_url(hps.redis.uri)
    max_size = hps.redis.max_size
    batch_size = hps.redis.batch_size

    ip_address = extract_ip_from_rtsp(source)
    is_stream = is_stream_source(source)

     # Get the camera ID based on the IP address
    camera_id = get_camera_id_from_ip(ip_address)
    if Path(source).is_file():
        key = Path(source).resolve().stem
    elif ip_address:
        # key = ip_address
        key = camera_id
    else:
        raise ValueError(f"Invalid source: {source}")

    cap = cv2.VideoCapture(source)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) % 100
    logger.info("Load source: {}, resolution: {}, fps: {}, stream: {}".format(
        source, (w, h), fps, is_stream
    ))

    n = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            time.sleep(hps.redis.time_retry)

            if not is_stream:
                logger.info("Not retry offline source: {}".format(source))
            else:
                # retry stream only
                logger.info("Retry streaming source: {} in {} seconds".format(source, hps.redis.time_retry))
                cap = cv2.VideoCapture(source)
                ret, frame = cap.read()

            continue

        # count
        n += 1
        if n != batch_size:  # read every batch frame
            continue

        while True:
            if redis_client.llen(key) < max_size:
                # Add frame count to the frame
                frame_with_count = {'frame_count': get_time(), 'frame_data': frame}
                redis_client.rpush(key, pickle.dumps(frame_with_count))
                break

        n = 0
        time.sleep(0.001)  # wait time


def extract_ip_from_rtsp(rtsp_url):
    # Define a regular expression pattern to match an IP address in the input string
    ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'

    # Use re.search to find the first IP address in the input string
    match = re.search(ip_pattern, rtsp_url)

    # Check if a match was found
    if match:
        # Extract the IP address from the match
        ip_address = match.group(1)
        return ip_address
    else:
        # If no match was found, return None or raise an error, depending on your preference
        return None


def is_stream_source(source):
    if ('rtsp://' in source) or ('tcp://' in source):
        return True

    if ('http://' in source) or ('https://' in source):
        return True

    return False

def get_camera_id_from_ip(ip_address):
    # Reverse lookup to find the camera ID based on the IP address
    for camera_id, camera_ip in CAMERA_IP_MAPPING.items():
        if camera_ip == ip_address:
            return camera_id
    return None
