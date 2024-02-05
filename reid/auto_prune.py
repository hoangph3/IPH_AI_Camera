# auto_prune_combined.py

from core.prune_log import PruneLogger
from utility.hparams import get_hparams_from_file

if __name__ == "__main__":
    prune_config = get_hparams_from_file("./env/prod.json")
    print("xdd")
    # Create instances for tracking and reid data
    tracking_pruner = PruneLogger(config=prune_config, data_type='tracking')
    reid_pruner = PruneLogger(config=prune_config, data_type='reid')

    # Run the pruning for both types
    tracking_pruner.run()
    reid_pruner.run()
