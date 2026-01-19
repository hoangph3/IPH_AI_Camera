from ultralytics import YOLO

# Load a model
model = YOLO("yolov5n.pt")  # load an official model


# Export the model
model.export(format="engine")
