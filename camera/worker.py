from loguru import logger
import pandas as pd

from utility.hparams import get_hparams_from_file, config_path
from utility.controller import PController
from utility.capture import read_frame_with_count


if __name__ == "__main__":
    hps = get_hparams_from_file(config_path)
    capture = PController.get_instance()

    # Current config
    hps = get_hparams_from_file(config_path, as_dict=True)
    sources: list = hps["camera"]

    sources = pd.DataFrame(sources).drop_duplicates('id').to_dict('records')

    # Run capture
    for source in sources:
        source_id = source['id']
        source_uri = source['uri']
        # E.g: source = {'id': 'cam1', 'uri': 'rtsp://...'}
        if source_id in capture.processes:  # running process
            continue
        capture.add_process(source_id, read_frame_with_count, (source_id, source_uri,))

    logger.info("Running process: {}".format(capture.processes))
