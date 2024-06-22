import itertools

# global parameters
MIN_SINGLE_CARDS = 5    # 最少单牌数量
MIN_PAIRS = 3           # 最少对子数量
MIN_TRIPLES = 2         # 最少三张数量

# action types
TYPE_0_PASS = 0             # 过
TYPE_1_SINGLE = 1           # 单牌
TYPE_2_PAIR = 2             # 对子
TYPE_3_TRIPLE = 3           # 三张
TYPE_4_BOMB = 4             # 炸弹
TYPE_5_KING_BOMB = 5        # 王炸
TYPE_6_3_1 = 6              # 三带一
TYPE_7_3_2 = 7              # 三带二
TYPE_8_SERIAL_SINGLE = 8    # 顺子
TYPE_9_SERIAL_PAIR = 9      # 连对
TYPE_10_SERIAL_TRIPLE = 10  # 飞机
TYPE_11_SERIAL_3_1 = 11     # 飞机带单
TYPE_12_SERIAL_3_2 = 12     # 飞机带双
TYPE_13_4_2 = 13            # 四带二
TYPE_14_4_22 = 14           # 四带两对
TYPE_15_WRONG = 15          # 错误牌型


# betting round action
PASS = 0    # 不叫
CALL = 1    # 叫地主
RAISE = 2   # 抢地主

# return all possible results of selecting num cards from cards list
def select(cards, num):
    return [list(i) for i in itertools.combinations(cards, num)]
