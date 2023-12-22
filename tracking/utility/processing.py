import cv2
from typing import Tuple
import numpy as np


def resize_with_pad(image: np.array, 
                    new_shape: Tuple[int, int], 
                    padding_color: Tuple[int] = (0, 0, 0)) -> np.array:
    """Maintains aspect ratio and resizes with padding.
    Params:
        image: Image to be resized.
        new_shape: Expected (width, height) of new image.
        padding_color: Tuple in BGR of padding color
    Returns:
        image: Resized image with padding
    """
    original_shape = (image.shape[1], image.shape[0])
    ratio = float(max(new_shape))/max(original_shape)
    new_size = tuple([int(x*ratio) for x in original_shape])

    if new_size[0] > new_shape[0] or new_size[1] > new_shape[1]:
        ratio = float(min(new_shape)) / min(original_shape)
        new_size = tuple([int(x * ratio) for x in original_shape])

    image = cv2.resize(image, new_size)
    delta_w = new_shape[0] - new_size[0] if new_shape[0] > new_size[0] else 0
    delta_h = new_shape[1] - new_size[1] if new_shape[1] > new_size[1] else 0
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)

    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT,None,value=padding_color)
    return image


def img_norm(x):
    x = (np.array(x) / 255.).astype(np.float32)
    return x


def L2_norm(features):
    features = features / np.linalg.norm(features, axis=1, keepdims=True)
    return features


def non_max_suppression(boxes, max_bbox_overlap, scores=None):
    """Suppress overlapping detections.

    Original code from [1]_ has been adapted to include confidence score.

    .. [1] http://www.pyimagesearch.com/2015/02/16/
           faster-non-maximum-suppression-python/

    Examples
    --------

        >>> boxes = [d.roi for d in detections]
        >>> scores = [d.confidence for d in detections]
        >>> indices = non_max_suppression(boxes, max_bbox_overlap, scores)
        >>> detections = [detections[i] for i in indices]

    Parameters
    ----------
    boxes : ndarray
        Array of ROIs (x, y, width, height).
    max_bbox_overlap : float
        ROIs that overlap more than this values are suppressed.
    scores : Optional[array_like]
        Detector confidence score.

    Returns
    -------
    List[int]
        Returns indices of detections that have survived non-maxima suppression.

    """
    if len(boxes) == 0:
        return []

    boxes = boxes.astype(np.float32)
    pick = []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2] + boxes[:, 0]
    y2 = boxes[:, 3] + boxes[:, 1]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    if scores is not None:
        idxs = np.argsort(scores)
    else:
        idxs = np.argsort(y2)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(
            idxs, np.concatenate(
                ([last], np.where(overlap > max_bbox_overlap)[0])))

    return pick


def delete_overlap_box(boxes, max_bbox_overlap, scores=None):
    if len(boxes) == 0:
        return []

    boxes = boxes.astype(np.float32)
    deleted = []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2] + boxes[:, 0]
    y2 = boxes[:, 3] + boxes[:, 1]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    if scores is not None:
        idxs = np.argsort(scores)
    else:
        idxs = np.argsort(y2)

    for i in range(len(idxs)):
        # last = len(idxs) - 1
        # i = idxs[last]
        # pick.append(i)

        xx1 = np.maximum(x1[idxs[i]], x1[idxs[i + 1:]])
        yy1 = np.maximum(y1[idxs[i]], y1[idxs[i + 1:]])
        xx2 = np.minimum(x2[idxs[i]], x2[idxs[i + 1:]])
        yy2 = np.minimum(y2[idxs[i]], y2[idxs[i + 1:]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[i + 1:]]
        if len(np.where(overlap > max_bbox_overlap)[0]) > 0:
            deleted += list(idxs[np.concatenate(([i], np.where(overlap > max_bbox_overlap)[0] + i + 1))])
    return list(set(idxs) - set(deleted))
