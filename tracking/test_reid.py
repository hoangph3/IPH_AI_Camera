import cv2
from ultralytics import YOLO
from utility import processing
from core.reid import ReIDMultiBackend


if __name__ == "__main__":
    reid_backend = ReIDMultiBackend(weights='checkpoint/osnet_x1_0_market.pt', device='cuda')
    det_model = YOLO(model='./checkpoint/yolov5mu.pt', task='detect')
    image = "./tests/pedestrian.jpg"
    image = cv2.imread(image)

    det_preds = det_model.predict(source=image, classes=[0, 1], verbose=True, conf=0.5)
    det_boxes = det_preds[0].boxes.data.cpu().numpy()

    # Get bounding boxes & scores
    scores = det_boxes[:, 4]
    bounding_boxes = det_boxes[:, 0:4]
    selected_indices = processing.non_max_suppression(boxes=bounding_boxes, max_bbox_overlap=0.3, scores=scores)
    bounding_boxes = bounding_boxes[selected_indices]

    print(det_boxes, bounding_boxes)
    features = reid_backend.get_features(xyxys=bounding_boxes, img=image, input_size=(64, 128))
    print(features.shape)
