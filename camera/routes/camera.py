from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
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

    # Add sources
    sources.extend(data.camera)
    sources = list(set(sources))

    hps["camera"] = sources
    content = {"camera": sources}
    create_hparams_to_file(config_path=config_path, config_data=hps)

    for source in sources:
        if source in capture.processes:  # running process
            continue
        capture.add_process(source, read_frame_with_count, (source,))

    logger.info("Running process: {}".format(capture.processes))

    return JSONResponse(content=content)


@camera.delete("/camera")
async def delete_camera(data: schema.Camera):
    hps = get_hparams_from_file(config_path, as_dict=True)
    sources = hps["camera"]

    for source in sources:
        if source not in data.camera:  # running process
            continue
        capture.kill_process(source, force=True)

    # Update sources
    sources = [source for source in sources if source not in data.camera]
    content = {"camera": sources}
    hps["camera"] = sources

    create_hparams_to_file(config_path=config_path, config_data=hps)

    logger.info("Running process: {}".format(capture.processes))

    return JSONResponse(content=content)
