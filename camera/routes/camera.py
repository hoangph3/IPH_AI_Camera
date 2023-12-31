from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import pandas as pd
from loguru import logger

from core import schema
from utility.hparams import get_hparams_from_file, create_hparams_to_file, config_path
from utility.controller import PController
from utility.capture import read_frame_with_count


camera = APIRouter(
    prefix="/api",
    tags=["camera"],
    responses={404: {"description": "Not found"}},
)
capture = PController.get_instance()


@camera.get("/camera")
async def get_camera():
    hps = get_hparams_from_file(config_path)
    content = {"camera": hps.camera}

    logger.info("Running process: {}".format(capture.processes))

    return JSONResponse(content=content)


@camera.post("/camera")
async def add_camera(data: schema.Camera):
    # Current config
    hps = get_hparams_from_file(config_path, as_dict=True)
    sources: list = hps["camera"]
    """
    E.g: sources = [
        {"id": "cam1", "uri": "rtsp://admin:kotora2023@192.168.0.149:8554/stream"},
        {"id": "cam2", "uri": "rtsp://admin:kotora2023@192.168.0.150:8554/stream"}
    ]
    """

    # Add sources
    sources.extend(data.camera)
    sources = pd.DataFrame(sources).drop_duplicates('id').to_dict('records')

    hps["camera"] = sources
    content = {"camera": sources}
    create_hparams_to_file(config_path=config_path, config_data=hps)

    for source in sources:
        source_id = source['id']
        source_uri = source['uri']
        # E.g: source = {'id': 'cam1', 'uri': 'rtsp://...'}
        if source_id in capture.processes:  # running process
            continue
        capture.add_process(source_id, read_frame_with_count, (source_id, source_uri,))

    logger.info("Running process: {}".format(capture.processes))

    return JSONResponse(content=content)


@camera.delete("/camera")
async def delete_camera(data: schema.Camera):
    hps = get_hparams_from_file(config_path, as_dict=True)
    sources = hps["camera"]
    valid_sources = {source['id']: source['uri'] for source in sources}

    for source in data.camera:
        source_id = source['id']
        if source_id not in valid_sources:  # not existed source
            continue
        try:
            capture.kill_process(source_id, force=True)
            valid_sources.pop(source_id, None)
        except Exception as e:
            logger.error(e)

    # Update sources
    save_sources = []
    for source_id, source_uri in valid_sources.items():
        save_sources.append({'id': source_id, 'uri': source_uri})

    content = {"camera": save_sources}
    hps["camera"] = save_sources

    create_hparams_to_file(config_path=config_path, config_data=hps)

    logger.info("Running process: {}".format(capture.processes))

    return JSONResponse(content=content)
