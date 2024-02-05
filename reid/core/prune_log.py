# core/prune.py

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
        self.prune_batch_size = self.config.prune_batch_size  # Update this line
        self.prune_period = self.config.period
        self.data_type = data_type

        # Configure the logger
        logger.add(f"prune_log_{data_type}_{time}.log", level="INFO")

    def run(self):
        while True:
            start_time = get_time()

            # Prune data based on the data type
            self.prune_data()

            # Log the next iteration
            end_time = get_time()
            process_time = end_time - start_time
            logger.info(f"Time took to delete {process_time} ms")
            logger.info("Waiting for the next iteration.")

    def prune_data(self):
        
        # Choose the appropriate method based on data_type
        if self.data_type == 'tracking':
            first_document = self.database.get_first_tracking_data()
            
        elif self.data_type == 'reid':
            first_document = self.database.get_first_reid_data()
        else:
            logger.error(f"Unsupported data type: {self.data_type}")
            return

        if first_document:
            first_timestamp_key = 'timestamp' if self.data_type == 'tracking' else 'query_time'
            
            first_timestamp = first_document.get(first_timestamp_key)
            print(first_timestamp)
            first_id = first_document.get('_id')

            prune_timedelta = timedelta(days=self.prune_period)
            prune_timestamp = datetime2time(time2datetime(get_time()) - prune_timedelta)

            if first_timestamp < prune_timestamp:
                # Delete documents in batches
                self.database.delete_data_batch(first_timestamp, self.data_type, self.prune_batch_size)
                

                formatted_prune_timestamp = time2datetime(prune_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Pruned {self.data_type} document {first_id} older than {formatted_prune_timestamp}")