from torch.utils.data import DataLoader
from online_triplet_loss.losses import batch_all_triplet_loss
import torch
import torch.optim as optim

from utility.dataset import ReIDDataset
from core.reid import ReIDMultiBackend


def train(model, device, train_loader, optimizer, epoch, margin):
    model.train()
    device = torch.device(device)

    for batch_idx, (data, labels) in enumerate(train_loader):
        data, labels = data.to(device), labels.to(device)

        optimizer.zero_grad()
        embeddings = model(data)

        loss, _ = batch_all_triplet_loss(labels, embeddings, margin=margin)

        loss.backward()
        optimizer.step()

        if batch_idx % 20 == 0:
            print(
                "Epoch {} Iteration {}: Loss = {}".format(
                    epoch, batch_idx, loss
                )
            )


if __name__ == "__main__":
    # Model
    device = 'cuda'
    reid_backend = ReIDMultiBackend(
        weights='./checkpoint/osnet_x1_0_market.pt',
        device=device, fp16=False
    )
    model = reid_backend.model

    # Optim
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Dataset
    data_dir = "/media/hoang/Data/aihub/tracking/IPH_WoB/train"
    dataset = ReIDDataset(data_dir=data_dir, target_size=(128, 256), random_state=42, k=10)
    data_loader = DataLoader(dataset, batch_size=128, shuffle=True)

    num_epochs = 1000
    margin = 1.0
    for epoch in range(1, num_epochs + 1):
        train(model, device, data_loader, optimizer, epoch, margin)
        torch.save(model.state_dict(), "osnet_x1_0_market_iph_wob.pt")
