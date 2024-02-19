from datetime import timedelta
import pandas as pd
import time

from utility.hparams import HParams
from utility.database import Database
from IPython.display import display
from utility import handler
from loguru import logger



class Report:
    def __init__(self, config: HParams) -> None:
        self.config = config
        self.database = Database(config=config)
        self.report_batch_time = config.backend.mongo.report.batch_time


    def run(self):
        batch_time = timedelta(hours=self.report_batch_time // 3600)
        idle_time = 5

        while True:
            last_reid_data = self.database.get_last_reid_data()
            last_reid_time = last_reid_data.get("query_time")

            # Not reid yet
            if last_reid_time is None:
                logger.info("Not reid: {}".format(last_reid_data))
                time.sleep(idle_time)
                continue

            last_report_data = self.database.get_last_report_data()
            last_report_time = last_report_data.get("end_time")

            # Not report yet
            if last_report_time is None:
                reid_data = self.database.get_history_reid_data(
                    time_from=None,
                    time_to=handler.get_time()
                )
                reid_data = sorted(reid_data, key=lambda d: d['query_time'])
                last_report_time = reid_data[0]['query_time']
                start_time = handler.time2datetime(last_report_time).replace(
                    minute=0, second=0
                )
            else:
                start_time = last_report_time.replace(
                    minute=0, second=0
                )

            end_time = handler.get_datetime()
            
            if end_time.minute == 0 and end_time.second == 0:
                end_time.replace(
                    minute=0, second=0
                )
                
                time_boxes = handler.split_time(
                    start_time=start_time,
                    end_time=end_time,
                    batch_time=batch_time
                )

                report_data = []
                for time_box in time_boxes:
                        datetime_from, datetime_to = time_box

                        time_from = handler.datetime2time(datetime_from)
                        time_to = handler.datetime2time(datetime_to)               
                        reid_batch_data = self.database.get_history_reid_data(
                            time_from=time_from, time_to=time_to
                        )
                        tracking_batch_data = self.database.get_history_tracking_data(
                            time_from=time_from, time_to=time_to
                        )

                        logger.info(
                            "Count: {} reid data from: {} to: {}".format(
                                len(reid_batch_data), datetime_from, datetime_to
                            )
                        )
                        
                        if not len(reid_batch_data):
                            # continue
                            
                            doc = {
                                'start_time': datetime_from,
                                'end_time': datetime_to,
                                'camera_counts': [],
                                'reid_counts': [],
                                'count': 0
                            }
                            report_data.append(doc)

                        reid_df = pd.DataFrame(reid_batch_data)
                        tracking_df = pd.DataFrame(tracking_batch_data)

                        camera_counts = {}
                        for cam_id, cam_df in tracking_df.groupby('camera_id'):
                            camera_counts[cam_id] = len(cam_df['object_id'].unique())

                        reid_counts = {}
                        for cam_id, cam_df in reid_df.groupby('query_cam'):
                            reid_counts[cam_id] = len(cam_df['global_id'].unique())

                        num_ids = len(reid_df['global_id'].unique())
                        doc = {
                            'start_time': datetime_from,
                            'end_time': datetime_to,
                            'camera_counts': camera_counts,
                            'reid_counts': reid_counts,
                            'count': num_ids
                        }
                        logger.info(
                            "Report from: {} to: {}: {}".format(
                                datetime_from, datetime_to, doc
                            )
                        )
                        report_data.append(doc)

                if len(report_data):
                    self.database.write_report_data(data=report_data)

                time.sleep(idle_time)
