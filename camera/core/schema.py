from pydantic import BaseModel
from typing import Union, List, Dict


class Camera(BaseModel):
    camera: List[Dict] = [
        {'id': 'cam1', 'uri': 'rtsp://192.168.1.1:8554/stream'},
        {'id': 'cam2', 'uri': 'rtsp://192.168.1.2:8554/stream'}
    ]
