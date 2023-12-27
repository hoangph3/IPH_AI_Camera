from core.report import Report
from utility.hparams import get_hparams_from_file


if __name__ == "__main__":
    config = get_hparams_from_file("./env/prod.json")
    reporter = Report(config=config)
    reporter.run()
