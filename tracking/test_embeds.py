from torch.utils.data import DataLoader
from scipy.spatial.distance import cdist
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np

from core.reid import ReIDMultiBackend
from utility.dataset import ReIDDataset
from utility.processing import L2_norm


def get_plot(encodings, ids, top_k=20, metric="euclidean", random_state=42):
    # Run reduce dimensions
    tsne = TSNE(n_components=2, random_state=random_state)
    embeddings_2d = tsne.fit_transform(encodings)

    for _id, encoding in zip(ids, encodings):
        encoding = np.expand_dims(encoding, 0)
        dist = cdist(encoding, encodings, metric)

        dist = dist[dist > 1e-9]
        sorted_indices = np.argsort(dist)

        top_k_values = dist[sorted_indices[:top_k]]
        top_k_indices = sorted_indices[:top_k]
        
        print("anchor:", _id)
        print("neighbor:", np.array(ids)[top_k_indices])
        print("dist:", top_k_values.round(6))
        print()

    # Plot
    plt.figure(figsize=(15, 10), facecolor='azure')
    for label in np.unique(ids):
        tmp = embeddings_2d[ids==label]
        c_x = np.sum([x for x, y in tmp]) / len(tmp)
        c_y = np.sum([y for x, y in tmp]) / len(tmp)
        plt.scatter(tmp[:,0], tmp[:,1], label=label)
        plt.annotate(label, (c_x, c_y))
    plt.legend()
    plt.show()


def get_embeds(
    data_loader: DataLoader,
    checkpoint_path=None,
    device=None,
    num_ids=10
):
    # Model
    reid_backend = ReIDMultiBackend(
        weights=checkpoint_path,
        device=device, fp16=False
    )
    model = reid_backend.model
    model.eval()

    encodings = []
    ids = []
    for batch_idx, (xb, yb) in enumerate(data_loader):
        if len(set(ids)) >= num_ids:
            break
        xb, yb = xb.to(device), yb.to(device)
        zb = model(xb)
        zb = L2_norm(zb.cpu().detach().numpy())
        for z, y in zip(zb, yb):
            encodings.append(z)
            ids.append(int(y))

    encodings = np.array(encodings)
    print(encodings.shape, ids)
    return encodings, ids


if __name__ == "__main__":
    np.set_printoptions(suppress=True)

    # Get data
    data_dir = "/media/hoang/Data/aihub/tracking/IPH_WoB/test"
    target_size = (128, 256)
    batch_size = 32
    random_state = 42

    # k below is num images, k=-1 is all images
    dataset = ReIDDataset(data_dir=data_dir, target_size=target_size, random_state=random_state, k=-1)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    # Get embeddings
    device = 'cuda'
    metric = 'euclidean'
    top_k = 20  # top k candidates
    num_ids = 15
    checkpoint_path = "./checkpoint/osnet_x1_0_market_iph_wob.pt"
    encodings, ids = get_embeds(data_loader=data_loader, checkpoint_path=checkpoint_path, device=device, num_ids=num_ids)

    get_plot(encodings=encodings, ids=ids, top_k=top_k, metric=metric, random_state=random_state)
