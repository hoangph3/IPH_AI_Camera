# core/prune_log.py

from datetime import timedelta
import time
from utility.handler import get_time, time2datetime, datetime2time
from utility.database import Database
from utility.hparams import HParams
from loguru import logger


class PruneLogger:
    def __init__(self, config: HParams, data_type):
        self.config = config
        self.database = Database(config=config)
        self.prune_period = self.config.period
        self.data_type = data_type

        # Configure the logger
        logger.add(f"prune_log_{data_type}_{time}.log", level="INFO")

    def run(self):
        while True:
            start_time = get_time()
            first_document = self.get_first_document()
            logger.info(self.data_type)
            if first_document:
                first_timestamp_key = (
                    "timestamp" if self.data_type == "tracking" else "query_time"
                )
                first_timestamp = first_document.get(first_timestamp_key)
                first_id = first_document.get("_id")
                # logger.info(first_timestamp)
                prune_timedelta = timedelta(days=self.prune_period)
                prune_timestamp = datetime2time(
                    time2datetime(get_time()) - prune_timedelta
                )

                if first_timestamp < prune_timestamp:
                    self.delete_data(first_document)
                    formatted_prune_timestamp = time2datetime(prune_timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    logger.info(
                        f"Pruned document {first_id} in {self.data_type} older than {formatted_prune_timestamp}"
                    )

            # Log the next iteration
            end_time = get_time()
            process_time = end_time - start_time
            logger.info(f"Time tooks to delete {process_time} ms")
            logger.info("Waiting for the next iteration.")
            time.sleep(1)

    def get_first_document(self):
        if self.data_type == "tracking":
            return self.database.get_first_tracking_data()
        elif self.data_type == "reid":
            return self.database.get_first_reid_data()
        else:
            logger.error(f"Unsupported data type: {self.data_type}")
            return None

    def delete_data(self, document):
        if self.data_type == "tracking":
            self.database.delete_tracking_data(document)
        elif self.data_type == "reid":
            self.database.delete_reid_data(document)
