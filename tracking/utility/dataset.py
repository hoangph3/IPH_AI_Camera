from torch.utils.data import Dataset
import cv2
import random
import os

from .dataio import convert_bgr2rgb
from .processing import img_norm, resize_with_pad, reshape_img


class ReIDDataset(Dataset):
    def __init__(
        self, data_dir="IPH_WoB", target_size=(128, 256), k=30, random_state=42
    ) -> None:
        self.data_dir = data_dir
        self.target_size = target_size
        self.k = k
        self.random_state = random_state
        self.encodings, self.ids = self.load()

    def load(self):
        data_dir = self.data_dir
        target_size = self.target_size
        random.seed(self.random_state)
        k = self.k

        encodings = []
        ids = []

        for user_id in sorted(os.listdir(data_dir)):

            _id = int(user_id)
            user_dir = os.path.join(data_dir, user_id)
            images = os.listdir(user_dir)
            random.shuffle(images)

            for image_path in images[:k]:
                image_path = os.path.join(user_dir, image_path)
                image_orig = cv2.imread(image_path)
                image_resize = resize_with_pad(image_orig, new_shape=target_size)

                # print(image_resize.shape)  # H x W x C
                image_resize = convert_bgr2rgb(image_resize)

                # target_size = (W x H)
                if (
                    image_resize.shape[0] != target_size[1]
                    or image_resize.shape[1] != target_size[0]
                ):
                    continue

                image_resize = img_norm(image_resize)
                image_resize = reshape_img(image_resize)  # N x C x H x W

                encodings.append(image_resize)
                ids.append(_id)

        return encodings, ids

    def __len__(self):
        return len(self.encodings)

    def __getitem__(self, index):
        return self.encodings[index], self.ids[index]
