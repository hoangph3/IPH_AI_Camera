from core.tracker import Tracker
from utility.hparams import get_hparams_from_file


if __name__ == "__main__":
    track_config = get_hparams_from_file("./env/prod.json")
    tracker = Tracker(config=track_config)

    camera_config = get_hparams_from_file("./env/camera.json", as_dict=True)
    tracker.run(
        camera_zone=camera_config["zone"]
    )
