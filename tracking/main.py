from core.tracker import Tracker
from core.detection import Detection
from utility.hparams import get_hparams_from_file


if __name__ == "__main__":
    config = get_hparams_from_file("./env/prod.json")

    if config.model.track.using:
        # Tracking mode
        worker = Tracker(config=config)
    else:
        # Object detection mode
        worker = Detection(config=config)

    camera_config = get_hparams_from_file("./env/camera.json", as_dict=True)
    worker.run(
        camera_zone=camera_config["zone"]
    )
