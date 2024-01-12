from boxmot.tracker_zoo import create_tracker
from loguru import logger
import torch
import redis
import pickle
import numpy as np

from collections import defaultdict
from core.reid import ReIDMultiBackend
from core.intersection import box_line_intersection, halve_bbox_y
from datalayer.mongo import MongoBackend
from utility import processing, handler, dataio
from utility.hparams import HParams
from core.detection import Detection


class Tracker(Detection):
    def build_trackers(self):
        trackers = {}
        keys = self.redis_client.keys('*')
        for key in keys:
            key = key.decode('utf-8')
            trackers[key] = create_tracker(
                tracker_type=self.config.model.track.track_type,
                tracker_config=self.config.model.track.track_config,
                reid_weights=self.config.model.reid.checkpoint,
                device=torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'),
                half=False,
                per_class=True
            )
        return trackers

    def run(self, camera_zone: dict):
        logger.info("Track start.")
        prev_frame_time = 0
        self.trackers = self.build_trackers()
        object_ids_per_tracker = defaultdict(lambda: defaultdict(list))
        excluded_ids = {}

        while True:
            track_events = []  # track_events need to be inserted to mongo
            try:
                keys = self.redis_client.keys('*')
                for key in keys:
                    # Get key name & data
                    key = key.decode('utf-8')

                    # Build new tracker
                    if key not in self.trackers:
                        # Init tracker
                        self.trackers[key] = create_tracker(
                            tracker_type=self.config.model.track.track_type,
                            tracker_config=self.config.model.track.track_config,
                            reid_weights=self.config.model.reid.checkpoint,
                            device=torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'),
                            half=False,
                            per_class=True
                        )
                    if key not in excluded_ids:
                        excluded_ids[key] = []

                    data = self.redis_client.lpop(key)

                    # Validate data
                    if data is None:
                        continue

                    frame_info = pickle.loads(data)
                    img = frame_info.get('frame_data')
                    timestamp = frame_info.get('frame_time')
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
                    tracks = self.trackers[key].update(det_boxes, img)
                    if not len(tracks):
                        continue

                    bounding_boxes = tracks[:, 0:4].astype(np.int32)
                    object_ids = tracks[:, 4].astype(np.int32)
                    scores = tracks[:, 5].astype(np.float32)

                    # Get embeddings
                    features = self.reid_model.get_features(
                        xyxys=bounding_boxes, img=img, input_size=self.reid_input_size
                    )

                    for xyxy, conf, feature, object_id in zip(bounding_boxes, scores, features, object_ids):
                        xyxy = xyxy.tolist()
                        x1, y1, x2, y2 = xyxy
                        object_id = int(object_id)
                        conf = round(float(conf), 4)
                        box_img = img[y1:y2, x1:x2]
                        height_img = img.shape[0]
                        upper, lower = halve_bbox_y(xyxy) 

                        # Filter box & camera zone
                        if (y2 > 2/3 * height_img) or (key not in camera_zone):
                            logger.info("Not valid box, cause y2: {}, max_y2: {}, cam: {}".format(
                                y2, 2/3*height_img, key
                            ))
                            excluded_ids[key].append(object_id)
                            continue
                        if object_id in excluded_ids[key]:
                            continue
                        line_intersect = camera_zone[key]['line_intersect']
                        box_time = camera_zone[key]['box_time']

                        bool_intersect_lower = box_line_intersection(lower, line_intersect)
                        bool_intersect_upper = box_line_intersection(upper, line_intersect)

                        if bool_intersect_lower and bool_intersect_upper == False:
                            waypath = 'Up'
                        elif bool_intersect_upper and bool_intersect_lower == False:
                            waypath = "Down"
                        else:
                            waypath = ''

                        if waypath != "Down":
                            continue

                        event = {
                            'camera_id': key,
                            'object_bbox': xyxy,
                            'confidence': conf,
                            'waypath': waypath,
                            'object_id': object_id,
                            'timestamp': timestamp,
                            'feature_embeddings': feature.tolist(),
                            'box_time': box_time,
                            'object_image': dataio.convert_numpy_array_to_bytes(
                                box_img
                            ) if self.config.model.track.save_crop else ''
                            # 'line_intersect': line_intersect,
                        }

                        if object_id in object_ids_per_tracker[key]:
                            continue

                        object_ids_per_tracker[key][object_id] = True
                        track_events.append(event)

                if len(track_events):
                    logger.info("Track: {} events".format(len(track_events)))
                    self.mongo_client.create(
                        db_name=self.mongo_database, collection_name=self.mongo_collection, data=track_events
                    )

            except Exception as e:
                logger.error("Track error: {}".format(e))
