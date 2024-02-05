# core/prune_log_tracking.py

from datetime import timedelta
from utility.handler import get_time, time2datetime, datetime2time
from utility.database import Database
from utility.hparams import HParams
from loguru import logger

class PruneLogger:
    def __init__(self, config: HParams):
        self.config = config
        self.database = Database(config=config)
        self.prune_period = self.config.period

        # Configure the logger
        logger.add("prune_log_tracking_{time}.log", level="INFO")

    def run(self):
        while True:
            start_time=get_time()
            first_document = self.database.get_first_tracking_data()
            if first_document:
                first_timestamp = first_document.get('timestamp')
                first_id =first_document.get('_id')
                
                
                prune_timedelta = timedelta(days=self.prune_period)
                prune_timestamp = datetime2time(time2datetime(get_time()) - prune_timedelta)

                if first_timestamp < prune_timestamp:
                    self.database.delete_tracking_data(first_document)
                    formatted_prune_timestamp = time2datetime(prune_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"Pruned document {first_id} in tracking older than {formatted_prune_timestamp}")

            # Log the next iteration
            end_time=get_time()
            process_time=end_time-start_time
            logger.info(f"Time tooks to delete {process_time} ms")
            logger.info(f"Waiting for the next iteration.")


