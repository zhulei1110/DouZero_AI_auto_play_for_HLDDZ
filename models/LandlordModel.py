import os

import torch
from torch import nn

from douzero.env.game_new import GameEnv
from douzero.evaluation.deep_agent_new import DeepAgent


def EnvToOnehot(cards):
    Env2IdxMap = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 8, 12: 9, 13: 10, 14: 11, 17: 12, 20: 13, 30: 14}
    cards = [Env2IdxMap[i] for i in cards]
    Onehot = torch.zeros((4, 15))
    for i in range(0, 15):
        Onehot[:cards.count(i), i] = 1
    return Onehot


def RealToOnehot(cards):
    RealCard2EnvCard = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6, 'T': 7, 'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12, 'X': 13, 'D': 14}
    cards = [RealCard2EnvCard[c] for c in cards]
    Onehot = torch.zeros((4, 15))
    for i in range(0, 15):
        Onehot[:cards.count(i), i] = 1
    return Onehot


# 这个类定义了一个多层全连接神经网络
# 网络包括六个全连接层和三个不同的 Dropout 层，用于防止过拟合
# 输入经过每一层和激活函数（ReLU）处理后，最终输出一个值
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
        x = torch.relu(self.dropout3(self.fc2(x)))
        x = torch.relu(self.dropout5(self.fc3(x)))
        x = torch.relu(self.dropout5(self.fc4(x)))
        x = torch.relu(self.dropout5(self.fc5(x)))
        x = self.fc6(x)
        return x
    

# 这个部分加载已经训练好的模型权重文件（如果存在），并将模型设置为评估模式
# 根据当前设备（CPU或GPU）加载模型权重
net = Net()
net.eval()
if os.path.exists("./weights/landlord_weights.pkl"):
    if torch.cuda.is_available():
        net.load_state_dict(torch.load('./weights/landlord_weights.pkl'))
    else:
        net.load_state_dict(torch.load('./weights/landlord_weights.pkl', map_location=torch.device("cpu")))
else:
    print("landlord_weights.pkl not found")


# 这个函数接收卡牌字符串，将其转换为 one-hot 编码
# 展平成一维向量，输入到模型中进行预测
# 输出预测结果（乘以 100 得到百分比形式）
def predict(cards):
    cards_onehot = torch.flatten(RealToOnehot(cards))
    y_predict = net(cards_onehot)
    return y_predict[0].item() * 100


ai_players = []
env = GameEnv(ai_players)


# 这个函数初始化 AI 玩家和游戏环境
# 使用指定路径的模型文件创建一个新的 DeepAgent 作为 “地主” 玩家
def init_model(model_path):
    global ai_players, env
    ai_players = ["landlord", DeepAgent("landlord", model_path)]
    env = GameEnv(ai_players)


# 这个函数与 init_model 类似
# 但它同时初始化两个不同模型路径的 AI 玩家
# 分别使用 model_path 和 wp_model_path
def init_model2(model_path, wp_model_path):
    global ai_players, env
    ai_players = ["landlord", DeepAgent("landlord", model_path)]
    ai_players2 = ["landlord", DeepAgent("landlord", wp_model_path)]
    env = GameEnv(ai_players, ai_players2)


# 这个函数使用模型进行预测
# 首先，定义所有可能的卡牌，然后将用户的手牌和 “地主” 三张底牌转换为环境中的卡牌表示
# 通过计算其他两位玩家的手牌，初始化游戏环境，进行一步模拟，并返回当前手牌的胜率
def predict_by_model(cards, llc):
    if len(cards) == 0 or cards is None:
        return 0
    
    AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7,
                  8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12,
                  12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]
    RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                        '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12,
                        'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}
    env.reset()

    other_hand_cards = []
    card_play_data_list = {}

    three_landlord_cards_env = [RealCard2EnvCard[card] for card in llc]
    user_hand_cards_env = [RealCard2EnvCard[card] for card in cards]

    three_landlord_cards_env.sort()
    user_hand_cards_env.sort()

    for i in set(AllEnvCard):
        other_hand_cards.extend([i] * (AllEnvCard.count(i) - user_hand_cards_env.count(i)))

    card_play_data_list.update({
        'three_landlord_cards': three_landlord_cards_env,
        "landlord": user_hand_cards_env,
        'landlord_up': other_hand_cards[0:17],
        'landlord_down': other_hand_cards[17:]
    })
    
    env.card_play_init(card_play_data_list)
    action_message, show_action_list = env.step("landlord")
    return action_message["win_rate"]

