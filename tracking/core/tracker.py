from ultralytics import YOLO
from loguru import logger
import torch
import redis
import pickle
import numpy as np

from core.reid import ReIDMultiBackend
from core.intersection import box_line_intersection, halve_bbox_y
from datalayer.mongo import MongoBackend
from utility import processing, handler, dataio
from utility.hparams import HParams


class Tracker:
    def __init__(self, config: HParams):
        # Backend
        self.redis_client = redis.Redis.from_url(config.backend.redis.uri)
        self.mongo_client = MongoBackend(config.backend.mongo.tracking.uri)
        self.mongo_database = config.backend.mongo.tracking.database
        self.mongo_collection = config.backend.mongo.tracking.collection

        # Model detect
        self.det_model = YOLO(model=config.model.detect.checkpoint, task='detect')
        self.det_conf = config.model.detect.conf
        self.det_overlap = config.model.detect.overlap
        self.det_classes = config.model.detect.classes

        # Model reid
        self.reid_model = ReIDMultiBackend(
            weights=config.model.reid.checkpoint,
            device='cuda' if torch.cuda.is_available() else 'cpu',
            fp16=config.model.reid.fp16
        )
        self.reid_input_size = config.model.reid.input_size  # (w, h)

    def run(self, camera_zone: dict):
        logger.info("Track start.")
        prev_frame_time = 0

        while True:
            track_events = []  # track_events need to be inserted to mongo
            try:
                keys = self.redis_client.keys('*')
                for key in keys:
                    # Get key name & data
                    key = key.decode('utf-8')
                    data = self.redis_client.lpop(key)

                    # Validate data
                    if data is None:
                        continue

                    frame_info = pickle.loads(data)
                    img = frame_info.get('frame_data')
                    frame_count = frame_info.get('frame_count')
                    if img is None:
                        continue

                    # Object detect
                    det_preds = self.det_model.predict(
                        source=img, classes=self.det_classes, verbose=True, conf=self.det_conf
                    )

                    # Compute fps
                    fps, prev_frame_time = handler.get_fps(prev_frame_time)
                    logger.info("FPS: {}".format(fps))

                    # Get bounding boxes & scores
                    det_boxes = det_preds[0].boxes.data.cpu().numpy()
                    if not len(det_boxes):
                        continue

                    scores = det_boxes[:, 4].astype(np.int32)
                    bounding_boxes = det_boxes[:, 0:4].astype(np.int32)
                    selected_indices = processing.non_max_suppression(
                        boxes=bounding_boxes, max_bbox_overlap=self.det_overlap, scores=scores
                    )
                    bounding_boxes = bounding_boxes[selected_indices]

                    # Get embeddings
                    features = self.reid_model.get_features(
                        xyxys=bounding_boxes, img=img, input_size=self.reid_input_size
                    )

                    for xyxy, conf, feature in zip(bounding_boxes, scores, features):
                        xyxy = xyxy.tolist()
                        conf = float(conf)
                        x1, y1, x2, y2 = xyxy
                        height_img = y2 - y1
                        box_img = img[y1:y2, x1:x2]
                        upper, lower = halve_bbox_y(xyxy) 

                        # Filter box & camera zone
                        if (y2 > 2/3 * height_img) or (key not in camera_zone):
                            continue

                        line_intersect = camera_zone[key]['line_intersect']
                        box_time = camera_zone[key]['box_time']

                        bool_intersect_lower = box_line_intersection(lower, line_intersect)
                        bool_intersect_upper = box_line_intersection(upper, line_intersect)

                        if bool_intersect_lower and bool_intersect_upper == False:
                            waypath = 'Up'
                        if bool_intersect_upper and bool_intersect_lower == False:
                            waypath = "Down"

                        event = {
                            'camera_id': key,
                            'object_bbox': xyxy,
                            'confidence': conf,
                            'waypath': waypath,
                            'frame_count': frame_count,
                            'timestamp': frame_count,
                            'box_time': box_time,
                            'line_intersect': line_intersect,
                            'feature_embeddings': feature.tolist(),
                            'object_image': dataio.convert_numpy_array_to_bytes(box_img),
                            # 'full_image': dataio.convert_numpy_array_to_bytes(img)
                        }

                        track_events.append(event)

                if len(track_events):
                    logger.info("Track: {} events".format(len(track_events)))
                    self.mongo_client.create(
                        db_name=self.mongo_database, collection_name=self.mongo_collection, data=track_events
                    )

            except Exception as e:
                logger.error("Track error: {}".format(e))
