import os

import torch
import torch.nn.functional as F

from torch import nn
from constants import EnvCard2IdxMap, RealCard2IdxMap


# 将环境中的卡牌列表转换为 Onehot 编码
def EnvToOnehot(cards):
    cards = [EnvCard2IdxMap[i] for i in cards]
    Onehot = torch.zeros((4, 15))
    for i in range(0, 15):
        Onehot[:cards.count(i), i] = 1
    return Onehot

# 将真实的卡牌字符转换为 Onehot 编码
def RealToOnehot(cards):
    cards = [RealCard2IdxMap[c] for c in cards]
    Onehot = torch.zeros((4, 15))
    for i in range(0, 15):
        Onehot[:cards.count(i), i] = 1
    return Onehot


# Net2 类是一个卷积神经网络（CNN），包括一个 1D 卷积层和多个全连接层，用于处理输入并生成输出
class Net2(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 16, kernel_size=(3,), padding=1)
        self.dense1 = nn.Linear(1020, 1024)
        self.dense2 = nn.Linear(1024, 512)
        self.dense3 = nn.Linear(512, 256)
        self.dense4 = nn.Linear(256, 128)
        self.dense5 = nn.Linear(128, 1)

    def forward(self, xi):
        x = xi.unsqueeze(1)
        x = F.leaky_relu(self.conv1(x))
        x = x.flatten(1, 2)
        x = torch.cat((x, xi), 1)
        x = F.leaky_relu(self.dense1(x))
        x = F.leaky_relu(self.dense2(x))
        x = F.leaky_relu(self.dense3(x))
        x = F.leaky_relu(self.dense4(x))
        x = self.dense5(x)
        x = torch.sigmoid(x)  # 在最后一层添加 Sigmoid 激活函数
        return x


# Net 类是一个全连接神经网络（FCNN），包括多个全连接层和 dropout 层，用于预测卡牌胜率
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(60, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, 512)
        self.fc4 = nn.Linear(512, 512)
        self.fc5 = nn.Linear(512, 512)
        self.fc6 = nn.Linear(512, 1)
        self.dropout5 = nn.Dropout(0.5)
        self.dropout3 = nn.Dropout(0.3)
        self.dropout1 = nn.Dropout(0.1)

    def forward(self, input):
        x = self.fc1(input)
        x = torch.relu(self.dropout1(self.fc2(x)))
        x = torch.relu(self.dropout3(self.fc3(x)))
        x = torch.relu(self.dropout5(self.fc4(x)))
        x = torch.relu(self.dropout5(self.fc5(x)))
        x = self.fc6(x)
        return x


# 初始化模型并检查是否使用 GPU
UseGPU = False
device = torch.device('cuda:0' if UseGPU and torch.cuda.is_available() else 'cpu')

net = Net()
net2 = Net2()

net.eval()
net2.eval()

if UseGPU:
    net = net.to(device)
    net2 = net2.to(device)

# 如果有权重文件，则加载这些权重文件
if os.path.exists("./weights/bid_weights.pkl"):
    if torch.cuda.is_available():
        net2.load_state_dict(torch.load('./weights/bid_weights.pkl'))
    else:
        net2.load_state_dict(torch.load('./weights/bid_weights.pkl', map_location = torch.device("cpu")))


# predict 函数将卡牌转换为 Onehot 编码，并使用 Net 模型预测胜率
def predict(cards):
    input = RealToOnehot(cards)
    if UseGPU:
        input = input.to(device)
    input = torch.flatten(input)
    win_rate = net(input)
    return win_rate[0].item() * 100

# predict_score 函数将卡牌转换为 Onehot 编码，并使用 Net2 模型预测胜率
def predict_score(cards):
    if len(cards) == 0 or cards is None:
        return 0
    
    input = RealToOnehot(cards)
    if UseGPU:
        input = input.to(device)
    input = torch.flatten(input)
    input = input.unsqueeze(0)
    result = net2(input)
    return result[0].item()

if __name__ == "__main__":
    print(predict_score("X2AKQJJ8777655443"))
    print(predict_score("X2AAQJ99887765553"))
