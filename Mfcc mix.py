说：
# -*- coding: utf-8 -*-
"""gtcc_ver2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bBtxGQxxopKMPhIaRuKd9Of7mVIGdyZy
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.metrics import precision_score, recall_score, accuracy_score
import torchvision.transforms as transforms

# 配置训练超参数
config = {
    'batch_size': 128,
    'learning_rate': 0.001,
    'num_epochs': 40,
    'num_workers': 2,
    'data_path': '/content/drive/MyDrive/gtcc_pool'
}

# 自定义数据集类
class GTCCDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.classes = sorted(os.listdir(root_dir))  # 获取所有主类别

        for label, class_name in enumerate(self.classes):
            class_dir = os.path.join(root_dir, class_name)
            if os.path.isdir(class_dir):
                for subdir in os.listdir(class_dir):  # 遍历子目录
                    subdir_path = os.path.join(class_dir, subdir)
                    if os.path.isdir(subdir_path):
                        for img_name in os.listdir(subdir_path):
                            img_path = os.path.join(subdir_path, img_name)
                            if img_path.endswith(('.png', '.jpg', '.jpeg')):
                                self.image_paths.append((img_path, label))

        # 8:2 按类别划分训练集和测试集
        self.train_data = []
        self.test_data = []

        classwise_data = {class_name: [] for class_name in self.classes}
        for img_path, label in self.image_paths:
            classwise_data[self.classes[label]].append((img_path, label))

        for class_name, images in classwise_data.items():
            split_idx = int(0.8 * len(images))
            self.train_data.extend(images[:split_idx])
            self.test_data.extend(images[split_idx:])

    def __len__(self):
        return len(self.train_data) + len(self.test_data)

    def __getitem__(self, idx):
        if idx < len(self.train_data):
            img_path, label = self.train_data[idx]
        else:
            img_path, label = self.test_data[idx - len(self.train_data)]

        image = Image.open(img_path).convert('L')  # 确保是灰度图
        if self.transform:
            image = self.transform(image)

        label = torch.tensor(label, dtype=torch.long)  # 转换为 Tensor
        return image, label

# 定义残差块
class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

        # 调整shortcut维度
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out

# 定义 CNN 模型
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, padding=1)  # 1通道（灰度图）
        self.bn1 = nn.BatchNorm2d(64)

        # 残差层
        self.layer1 = nn.Sequential(
            ResBlock(64, 64),
            ResBlock(64, 64)
        )
        self.layer2 = nn.Sequential(
            ResBlock(64, 128, stride=2),  # 降采样
            ResBlock(128, 128)
        )
        self.layer3 = nn.Sequential(
            ResBlock(128, 256, stride=2),  # 降采样
            ResBlock(256, 256)
        )

        # 计算展平后的特征尺寸（适配 100x39）
        self.fc_layers = nn.Sequential(
            nn.Linear(256 * 10 * 25, 512),  # 计算展平尺寸
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.55),
            nn.Linear(512, 4)  # 4 类分类
        )

    def forward(self, x):
        x = torch.relu(self.bn1(self.conv1(x)))
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.view(x.size(0), -1)  # 展平
        x = self.fc_layers(x)
        return x

# 加载数据集
dataset = GTCCDataset(root_dir=config['data_path'], transform=transform)

# 创建数据加载器
train_loader = DataLoader(dataset, batch_size=config['batch_size'], shuffle=True, num_workers=config['num_workers'])
test_loader = DataLoader(dataset, batch_size=100, shuffle=False, num_workers=config['num_workers'])

# 打印类别信息
print("类别列表:", dataset.classes)

# 打印一个样本数据检查
sample_image_path, sample_label = dataset.train_data[0]
sample_image_tensor = transform(Image.open(sample_image_path))  # 转换为张量
print("样本图像形状:", sample_image_tensor.shape, "标签:", sample_label)

# 设置计算设备（GPU/CPU）
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 初始化模型、损失函数和优化器
model = CNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=config['learning_rate'])

# 设置学习率调度器
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=25, gamma=0.15)

# 初始化性能指标记录列表
train_losses = []
train_accuracies = []
test_accuracies = []
test_precisions = []
test_recalls = []

# 训练模型的函数
def train_model():
    global train_losses, train_accuracies, test_accuracies
    model.train()
    for epoch in range(config['num_epochs']):
        running_loss = 0.0
        correct = 0
        total = 0
        all_preds = []
        all_labels = []

        # 训练循环
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)  # labels 现在是 Tensor
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

        epoch_loss = running_loss / len(train_loader)
        accuracy = correct / total
        precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
        recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)

        train_losses.append(epoch_loss)
        train_accuracies.append(accuracy)

        model.eval()
        test_correct = 0
        test_total = 0
        test_all_preds = []
        test_all_labels = []

        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()
                test_all_preds.extend(predicted.cpu().numpy())
                test_all_labels.extend(labels.cpu().numpy())

        test_accuracy = test_correct / test_total
        test_precision = precision_score(test_all_preds, test_all_labels, average='weighted', zero_division=0)
        test_recall = recall_score(test_all_preds, test_all_labels, average='weighted', zero_division=0)
        test_accuracies.append(test_accuracy)
        test_precisions.append(test_precision)
        test_recalls.append(test_recall)
        model.train()
        scheduler.step()

        print(f'Epoch [{epoch + 1}/{config["num_epochs"]}], Loss: {epoch_loss:.4f}, Train Acc: {accuracy*100:.2f}%, Test Acc: {test_accuracy*100:.2f}%, Test Precision: {test_precision:.4f}, Test Recall: {test_recall:.4f}')


# 绘制训练过程的可视化图表
def plot_metrics():
    epochs = range(1, config['num_epochs'] + 1)

    # 绘制损失曲线
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.plot(epochs, train_losses, label='Training Loss', color='blue')
    plt.title('Training Loss Curve')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')

    # 绘制准确率曲线
    plt.subplot(2, 2, 2)
    plt.plot(epochs, train_accuracies, label='Training Accuracy', color='green')
    plt.plot(epochs, test_accuracies, label='Test Accuracy', color='red')
    plt.title('Accuracy Curve')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # 绘制精确率曲线
    plt.subplot(2, 2, 3)
    plt.plot(epochs, test_precisions, label='Test Precision', color='purple')
    plt.title('Test Precision Curve')
    plt.xlabel('Epochs')
    plt.ylabel('Precision')

    # 绘制召回率曲线
    plt.subplot(2, 2, 4)
    plt.plot(epochs, test_recalls, label='Test Recall', color='orange')
    plt.title('Test Recall Curve')
    plt.xlabel('Epochs')
    plt.ylabel('Recall')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    train_model()
    plot_metrics()