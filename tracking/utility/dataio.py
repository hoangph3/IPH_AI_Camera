from PIL import Image
import numpy as np
import tempfile
import cv2
import base64
import io


def convert_img_to_numpy_array(img_path, resize=False, image_width=None):
    # TODO: load image from directory and convert to numpy array
    img = Image.open(img_path)
    img.convert("RGB").save(img_path, "JPEG")
    img = Image.open(img_path)

    # resize with aspect ratio
    if resize is True:
        if not isinstance(image_width, int):
            raise ValueError("Require image width as a integer!")
        new_width = image_width
        if max([img.height, img.width]) > new_width:
            aspect_ratio = img.height / img.width
            new_height = new_width * aspect_ratio
            img = img.resize((int(new_width), int(new_height)))

    # convert to array
    array = np.asarray(img)
    return array


def convert_numpy_array_to_bytes(array: np.array) -> str:
    array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    # TODO: convert numpy array to bytes
    compressed_file = io.BytesIO()
    Image.fromarray(array).save(compressed_file, format="JPEG")
    compressed_file.seek(0)
    return base64.b64encode(compressed_file.read()).decode()


def convert_img_to_bytes(img_path):
    # TODO: convert img to bytes
    array = convert_img_to_numpy_array(img_path)
    return convert_numpy_array_to_bytes(array)


def convert_bytes_to_numpy_array(j_dumps: str, resize=False, image_width=None) -> np.array:
    # TODO: load json string to numpy array
    compressed_data = base64.b64decode(j_dumps)
    img = Image.open(io.BytesIO(compressed_data))

    # convert PNG -> JPEG
    img_path = tempfile.NamedTemporaryFile(suffix='.jpg').name
    img.convert("RGB").save(img_path, "JPEG")
    img = Image.open(img_path)

    # resize with aspect ratio
    if resize is True:
        if not isinstance(image_width, int):
            raise ValueError("Require image width as a integer!")
        new_width = image_width
        if max([img.height, img.width]) > new_width:
            aspect_ratio = img.height / img.width
            new_height = new_width * aspect_ratio
            img = img.resize((int(new_width), int(new_height)))

    return np.array(img)
