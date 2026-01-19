from datetime import timedelta
import pandas as pd
import time

from utility.hparams import HParams
from utility.database import Database
from utility import handler
from loguru import logger


class Report:
    def __init__(self, config: HParams) -> None:
        self.config = config
        self.database = Database(config=config)
        self.report_batch_time = config.backend.mongo.report.batch_time  # seconds

    def run(self):
        batch_time = timedelta(seconds=self.report_batch_time)
        idle_time = 5

        while True:
            try:
                # =========================
                # 1. Get last reid time
                # =========================
                last_reid_data = self.database.get_last_reid_data()
                last_reid_time = last_reid_data.get("query_time")

                if last_reid_time is None:
                    logger.info("Not reid yet")
                    time.sleep(idle_time)
                    continue

                # =========================
                # 2. Get last report time
                # =========================
                last_report_data = self.database.get_last_report_data()
                last_report_time = last_report_data.get("end_time")

                # =========================
                # 3. Current hour (rounded)
                # =========================
                now = handler.get_datetime().replace(minute=0, second=0, microsecond=0)

                # Trigger only when reach hour boundary
                if handler.get_datetime().minute != 0:
                    time.sleep(idle_time)
                    continue

                # =========================
                # 4. Init start_time
                # =========================
                if last_report_time is None:
                    # First time: align to first reid hour
                    start_time = handler.time2datetime(last_reid_time).replace(
                        minute=0, second=0, microsecond=0
                    )
                else:
                    start_time = last_report_time

                # No new batch
                if start_time >= now:
                    time.sleep(idle_time)
                    continue

                # =========================
                # 5. Split time boxes
                # =========================
                time_boxes = handler.split_time(
                    start_time=start_time, end_time=now, batch_time=batch_time
                )

                report_data = []

                for datetime_from, datetime_to in time_boxes:
                    time_from = handler.datetime2time(datetime_from)
                    time_to = handler.datetime2time(datetime_to)

                    reid_batch_data = self.database.get_history_reid_data(
                        time_from=time_from, time_to=time_to
                    )

                    tracking_batch_data = self.database.get_history_tracking_data(
                        time_from=time_from, time_to=time_to
                    )

                    logger.info(
                        f"Count: {len(reid_batch_data)} reid data "
                        f"from: {datetime_from} to: {datetime_to}"
                    )

                    if not reid_batch_data:
                        doc = {
                            "start_time": datetime_from,
                            "end_time": datetime_to,
                            "camera_counts": {},
                            "reid_counts": {},
                            "count": 0,
                        }
                        report_data.append(doc)
                        continue

                    reid_df = pd.DataFrame(reid_batch_data)
                    tracking_df = pd.DataFrame(tracking_batch_data)

                    camera_counts = {
                        cam: len(df["object_id"].unique())
                        for cam, df in tracking_df.groupby("camera_id")
                    }

                    reid_counts = {
                        cam: len(df["global_id"].unique())
                        for cam, df in reid_df.groupby("query_cam")
                    }

                    num_ids = reid_df["global_id"].nunique()

                    doc = {
                        "start_time": datetime_from,
                        "end_time": datetime_to,
                        "camera_counts": camera_counts,
                        "reid_counts": reid_counts,
                        "count": num_ids,
                    }

                    logger.info(
                        f"Report from: {datetime_from} to: {datetime_to}: {doc}"
                    )

                    report_data.append(doc)

                # =========================
                # 6. Write report
                # =========================
                if report_data:
                    self.database.write_report_data(report_data)

            except Exception as e:
                logger.exception(f"Report error: {e}")

            time.sleep(idle_time)
