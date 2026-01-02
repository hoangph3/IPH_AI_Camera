import time
from core.prune_log import PruneLogger
from utility.hparams import get_hparams_from_file
import threading


if __name__ == "__main__":
    prune_config = get_hparams_from_file("./env/prod.json")

    # Create instances for tracking and reid data
    tracking_pruner = PruneLogger(config=prune_config, data_type='tracking')
    reid_pruner = PruneLogger(config=prune_config, data_type='reid')

    # Create threads for simultaneous execution
    tracking_thread = threading.Thread(target=tracking_pruner.run)
    reid_thread = threading.Thread(target=reid_pruner.run)
    
    # Start the threads
    reid_thread.start()
    tracking_thread.start()
   
# # Simulate running for a while
#     time.sleep(1)  # Let the threads run for 10 seconds

#     # Stop the threads
#     tracking_pruner.stop()
#     reid_pruner.stop()

    # # Wait for both threads to finish
    # tracking_thread.join()
    # reid_thread.join()
    
    # print("Both threads have finished.")
    
    # # Wait for both threads to finish
    # tracking_thread.join()
    # reid_thread.join()
