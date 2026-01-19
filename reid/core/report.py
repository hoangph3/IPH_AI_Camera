from datetime import timedelta
import pandas as pd
import time

from utility.hparams import HParams
from utility.database import Database
from utility import handler
from loguru import logger


# =========================
# Time helpers (CRITICAL)
# =========================
def floor_to_hour(dt):
    return dt.replace(minute=0, second=0, microsecond=0)


class Report:
    def __init__(self, config: HParams) -> None:
        self.config = config
        self.database = Database(config=config)
        self.batch = timedelta(hours=1)
        self.idle_time = 5

    def run(self):
        logger.info("===== REPORT SERVICE STARTED =====")

        while True:
            try:
                logger.info("----- LOOP TICK -----")

                # =========================
                # 1. LAST REID
                # =========================
                last_reid_data = self.database.get_last_reid_data()
                logger.info(f"last_reid_data(raw) = {last_reid_data}")

                last_reid_time = (
                    last_reid_data.get("query_time") if last_reid_data else None
                )
                logger.info(f"last_reid_time = {last_reid_time}")

                if last_reid_time is None:
                    logger.warning("NO LAST REID TIME -> SLEEP")
                    time.sleep(self.idle_time)
                    continue

                last_reid_dt_raw = handler.time2datetime(last_reid_time)
                last_reid_dt = floor_to_hour(last_reid_dt_raw)

                logger.info(
                    f"last_reid_dt_raw = {last_reid_dt_raw}, "
                    f"last_reid_dt(floor) = {last_reid_dt}"
                )

                # =========================
                # 2. LAST REPORT
                # =========================
                last_report_data = self.database.get_last_report_data()
                logger.info(f"last_report_data(raw) = {last_report_data}")

                last_report_time_raw = (
                    last_report_data.get("end_time") if last_report_data else None
                )
                logger.info(f"last_report_time_raw = {last_report_time_raw}")

                if last_report_time_raw is not None:
                    last_report_time = floor_to_hour(last_report_time_raw)
                    drift_ms = (
                        last_report_time_raw - last_report_time
                    ).total_seconds() * 1000
                    logger.warning(
                        f"Normalize last_report_time: "
                        f"{last_report_time_raw} -> {last_report_time} "
                        f"(drift={drift_ms:.3f} ms)"
                    )
                else:
                    last_report_time = None
                    logger.info("NO LAST REPORT FOUND")

                # =========================
                # 3. NOW & REPORTABLE END
                # =========================
                now = handler.get_datetime()
                reportable_end = floor_to_hour(now)

                logger.info(f"now = {now}")
                logger.info(f"reportable_end = {reportable_end}")

                # =========================
                # 4. START TIME
                # =========================
                if last_report_time is None:
                    start_time = last_reid_dt
                    logger.info("NO LAST REPORT -> start_time = last_reid_dt")
                else:
                    start_time = last_report_time
                    logger.info("FOUND LAST REPORT -> start_time = last_report_time")

                start_time = floor_to_hour(start_time)
                logger.info(f"start_time(normalized) = {start_time}")

                # =========================
                # 5. BACKDATE LOOP
                # =========================
                current_start = start_time
                loop_idx = 0

                while True:
                    current_end = current_start + self.batch

                    logger.info(
                        f"[CHECK] interval {loop_idx}: "
                        f"{current_start} -> {current_end}"
                    )
                    logger.info(
                        f"[COND] current_end <= reportable_end ? "
                        f"{current_end} <= {reportable_end} "
                        f"= {current_end <= reportable_end}"
                    )

                    if current_end > reportable_end:
                        logger.info("BREAK: interval exceeds reportable_end")
                        break

                    time_from = handler.datetime2time(current_start)
                    time_to = handler.datetime2time(current_end)

                    logger.info(f"[QUERY] time_from={time_from}, time_to={time_to}")

                    reid_batch_data = self.database.get_history_reid_data(
                        time_from=time_from, time_to=time_to
                    )
                    tracking_batch_data = self.database.get_history_tracking_data(
                        time_from=time_from, time_to=time_to
                    )

                    logger.info(
                        f"[DATA] reid_count={len(reid_batch_data)}, "
                        f"tracking_count={len(tracking_batch_data)}"
                    )

                    # =========================
                    # BUILD REPORT DOC
                    # =========================
                    if not reid_batch_data:
                        logger.warning("NO REID DATA -> WRITE EMPTY REPORT")
                        doc = {
                            "start_time": current_start,
                            "end_time": current_end,
                            "camera_counts": {},
                            "reid_counts": {},
                            "count": 0,
                        }
                    else:
                        reid_df = pd.DataFrame(reid_batch_data)
                        tracking_df = pd.DataFrame(tracking_batch_data)

                        logger.info(
                            f"reid_df.shape={reid_df.shape}, "
                            f"tracking_df.shape={tracking_df.shape}"
                        )

                        camera_counts = (
                            {
                                cam: len(df["object_id"].unique())
                                for cam, df in tracking_df.groupby("camera_id")
                            }
                            if not tracking_df.empty
                            else {}
                        )

                        reid_counts = {
                            cam: len(df["global_id"].unique())
                            for cam, df in reid_df.groupby("query_cam")
                        }

                        doc = {
                            "start_time": current_start,
                            "end_time": current_end,
                            "camera_counts": camera_counts,
                            "reid_counts": reid_counts,
                            "count": reid_df["global_id"].nunique(),
                        }

                    logger.info(f"[WRITE] doc = {doc}")

                    # =========================
                    # WRITE (IDEMPOTENT)
                    # =========================
                    self.database.write_report_data([doc])

                    logger.info(f"[DONE] interval {current_start} -> {current_end}")

                    current_start = current_end
                    loop_idx += 1

            except Exception as e:
                logger.exception(f"REPORT ERROR: {e}")

            logger.info(f"SLEEP {self.idle_time}s\n")
            time.sleep(self.idle_time)
