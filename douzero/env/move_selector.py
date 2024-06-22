# return all moves that can beat rivals, moves and rival_move should be same type
import collections

# 这个函数用于处理 单张牌、对子、三张牌 和 炸弹 的情况
# 它将所有大于对手出牌的牌组合加入到新列表中并返回
def common_handle(moves, rival_move):
    new_moves = list()
    for move in moves:
        if move[0] > rival_move[0]:
            new_moves.append(move)
    return new_moves

# 以下4个函数分别处理 单张牌、对子、三张牌 和 炸弹
# 它们都调用 common_handle 函数，因为这些类型的比较逻辑相同，只需要比较第一张牌的大小
def filter_type_1_single(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_2_pair(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_3_triple(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_4_bomb(moves, rival_move):
    return common_handle(moves, rival_move)

# No need to filter for type_5_king_bomb

# 这个函数处理 三带一 的情况
# 它先对对手的出牌排序，并获取三张牌中的中间牌作为 rival_rank
# 然后比较自己出牌中的三张牌的中间牌，如果比 rival_rank 大，则加入新列表中
def filter_type_6_3_1(moves, rival_move):
    rival_move.sort()
    rival_rank = rival_move[1]
    new_moves = list()
    for move in moves:
        move.sort()
        my_rank = move[1]
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves

# 这个函数处理 三带二 的情况
# 它的逻辑与 filter_type_6_3_1 类似，但比较的是三张牌中的最大牌
def filter_type_7_3_2(moves, rival_move):
    rival_move.sort()
    rival_rank = rival_move[2]
    new_moves = list()
    for move in moves:
        move.sort()
        my_rank = move[2]
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves

# 以下3个函数分别处理 顺子、连对 和 飞机
# 它们调用 common_handle 函数，因为这些类型的比较逻辑相同，只需要比较第一张牌的大小
def filter_type_8_serial_single(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_9_serial_pair(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_10_serial_triple(moves, rival_move):
    return common_handle(moves, rival_move)

# 以下2个函数处理 飞机带单 和 飞机带双
# 它们首先使用 collections.Counter 统计牌的数量，并找到三张牌中最大的牌，然后比较大小
def filter_type_11_serial_3_1(moves, rival_move):
    rival = collections.Counter(rival_move)
    rival_rank = max([k for k, v in rival.items() if v == 3])
    new_moves = list()
    for move in moves:
        mymove = collections.Counter(move)
        my_rank = max([k for k, v in mymove.items() if v == 3])
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves

def filter_type_12_serial_3_2(moves, rival_move):
    rival = collections.Counter(rival_move)
    rival_rank = max([k for k, v in rival.items() if v == 3])
    new_moves = list()
    for move in moves:
        mymove = collections.Counter(move)
        my_rank = max([k for k, v in mymove.items() if v == 3])
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves

# 这个函数处理 四带二 的情况
# 它的逻辑与filter_type_6_3_1类似，但比较的是四张牌中的第二大牌
def filter_type_13_4_2(moves, rival_move):
    rival_move.sort()
    rival_rank = rival_move[2]
    new_moves = list()
    for move in moves:
        move.sort()
        my_rank = move[2]
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves

# 这个函数处理 四带两对 的情况
# 它使用 collections.Counter 找到对手和自己的四张牌的最大牌，并比较大小
def filter_type_14_4_22(moves, rival_move):
    rival = collections.Counter(rival_move)
    rival_rank = my_rank = 0
    for k, v in rival.items():
        if v == 4:
            rival_rank = k
    new_moves = list()
    for move in moves:
        mymove = collections.Counter(move)
        for k, v in mymove.items():
            if v == 4:
                my_rank = k
        if my_rank > rival_rank:
            new_moves.append(move)
    return new_moves
