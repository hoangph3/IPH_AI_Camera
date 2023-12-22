import torch
import torch.nn as nn
import numpy as np

from nnet.backbones import build_model, get_model_name, load_pretrained_weights, get_nr_classes
from utility.processing import L2_norm, img_norm, resize_with_pad
import cv2
import os


class ReIDMultiBackend(nn.Module):
    # ReID models MultiBackend class for python inference on various backends
    def __init__(
        self, weights: str, device='cpu', fp16=False
    ):
        super().__init__()
        self.device = torch.device(device)
        self.fp16 = fp16

        # Build model
        model_name = get_model_name(weights)
        self.model = build_model(
            model_name,
            num_classes=get_nr_classes(weights),
            pretrained=not (weights and os.path.exists(weights)),
            use_gpu=device,
        )
        self.session = None
        self.model_type = None

        # Load weights
        if weights.endswith('.pt') or weights.endswith('.pth'):
            self.model_type = "torch"
            self.model = load_pretrained_weights(self.model, weights)
            self.model.to(device).eval()  # set eval mode
            self.model.half() if self.fp16 else self.model.float()
        elif weights.endswith('.onnx'):  # ONNX Runtime
            self.model_type = "onnx"
            cuda = torch.cuda.is_available() and device.type != "cpu"
            import onnxruntime
            providers = (
                ["CUDAExecutionProvider", "CPUExecutionProvider"]
                if cuda
                else ["CPUExecutionProvider"]
            )
            self.session = onnxruntime.InferenceSession(weights, providers=providers)
        else:
            raise ValueError("This model framework is not supported yet!")

    def preprocess(self, xyxys, img, input_size):
        crops = []
        # dets are of different sizes so batch preprocessing is not possible
        for box in xyxys:
            x1, y1, x2, y2 = box.astype('int')
            crop = img[y1:y2, x1:x2]
            crop = resize_with_pad(crop, new_shape=input_size)
            # Filter shape
            if crop.shape[0] != input_size[0] or crop.shape[1] != input_size[1]:
                continue
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            # Normalize image
            crop = img_norm(crop)
            crop = torch.from_numpy(crop).float()
            crops.append(crop)

        crops = torch.stack(crops, dim=0)
        crops = torch.permute(crops, (0, 3, 1, 2))
        crops = crops.to(dtype=torch.half if self.fp16 else torch.float, device=self.device)

        return crops

    def forward(self, im_batch):
        # batch to half
        if self.fp16 and im_batch.dtype != torch.float16:
            im_batch = im_batch.half()

        # batch processing
        features = []
        if self.model_type == "torch":
            features = self.model(im_batch)
        elif self.model_type == "onnx":  # ONNX Runtime
            im_batch = im_batch.cpu().numpy()  # torch to numpy
            features = self.session.run(
                [self.session.get_outputs()[0].name],
                {self.session.get_inputs()[0].name: im_batch},
            )[0]
        else:
            raise ValueError("Framework not supported at the moment, leave an enhancement suggestion")

        if isinstance(features, (list, tuple)):
            return (
                self.to_numpy(features[0]) if len(features) == 1 else [self.to_numpy(x) for x in features]
            )
        else:
            return self.to_numpy(features)

    def to_numpy(self, x):
        return x.cpu().numpy() if isinstance(x, torch.Tensor) else x

    @torch.no_grad()
    def get_features(self, xyxys, img, input_size=(128, 256)):
        if xyxys.size != 0:
            crops = self.preprocess(xyxys, img, input_size)
            features = self.forward(crops)
        else:
            features = np.array([])
        
        # Normalize vector
        features = L2_norm(features)
        return features
