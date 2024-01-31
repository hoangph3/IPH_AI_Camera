from core.prune_log_reid import PruneLogger
from utility.hparams import get_hparams_from_file


if __name__ == "__main__":
    prune_config = get_hparams_from_file("./env/prod.json")
    pruner = PruneLogger(config=prune_config)

    pruner.run()
