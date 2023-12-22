from core.matching import Matching
from utility.hparams import get_hparams_from_file


if __name__ == "__main__":
    matching_config = get_hparams_from_file("./env/prod.json")
    matcher = Matching(config=matching_config)
    matcher.run()
