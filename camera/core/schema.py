from pydantic import BaseModel
from typing import Union, List


class Camera(BaseModel):
    camera: List[str]
