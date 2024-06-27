from copy import deepcopy

from . import move_detector as md, move_selector as ms
from .move_generator import MovesGener

from constants import EnvCard2RealCard, AllEnvCard, Bombs
from utils import search_actions, select_optimal_path, check_42

class GameEnv(object):
    def __init__(self, players):
        self.game_infoset = None            # 当前游戏信息集
        self.card_play_action_seq = []      # 出牌动作序列

        self.three_landlord_cards = None    # 三张底牌
        self.game_over = False              # 游戏是否结束

        self.acting_player_position = None  # 当前正在行动的玩家位置
        self.player_utility_dict = None     # 玩家得分的字典

        self.players = players              # 玩家列表

        self.model_type = ""                # 模型类型

        self.last_move_dict = {             # 最后一次出牌的记录
            'landlord': [],
            'landlord_up': [],
            'landlord_down': []
        }

        self.played_cards = {               # 已出牌的记录
            'landlord': [],
            'landlord_up': [],
            'landlord_down': []
        }

        self.last_move = []                 # 最后一次出牌
        self.last_two_moves = []            # 最后两次出牌

        self.num_wins = {                   # 玩家胜利次数记录
            'landlord': 0,
            'farmer': 0
        }

        self.num_scores = {                 # 玩家得分记录
            'landlord': 0,
            'farmer': 0
        }

        self.info_sets = {                  # 玩家信息集
            'landlord': InfoSet('landlord'),
            'landlord_up': InfoSet('landlord_up'),
            'landlord_down': InfoSet('landlord_down')
        }

        self.bomb_num = 0                   # 炸弹数量
        self.last_pid = 'landlord'          # 最后一个有效出牌的玩家位置

        self.bid_info = [                   # 叫地主的信息
            [1, 0.5, 1],
            [1, 1, 1],
            [1, 1, -4],
            [1, 1, 1]
        ]

        self.multiply_info = [1, 1, 1]      # 倍数信息
        self.bid_count = 0                  # 叫地主次数
        self.multiply_count = {             # 倍数计数
            'landlord': 1,
            'landlord_up': 1,
            'landlord_down': 1
        }

        self.step_count = 0                 # 步数计数

    def card_play_init(self, card_play_data):
        self.info_sets['landlord'].player_hand_cards = card_play_data['landlord']
        self.info_sets['landlord_up'].player_hand_cards = card_play_data['landlord_up']
        self.info_sets['landlord_down'].player_hand_cards = card_play_data['landlord_down']
        self.three_landlord_cards = card_play_data['three_landlord_cards']

        self.get_acting_player_position()
        self.game_infoset = self.get_infoset()

    def check_if_game_overed(self):
        # 如果地主、上家或下家中有任何一家的手牌数量为零，即表示有玩家已经出完了手中的牌
        if len(self.info_sets['landlord'].player_hand_cards) == 0 or \
            len(self.info_sets['landlord_up'].player_hand_cards) == 0 or \
                len(self.info_sets['landlord_down'].player_hand_cards) == 0:

            self.compute_player_utility()   # 计算玩家的效用（得分或者胜利情况）
            self.update_num_wins_scores()   # 更新胜局数和分数等游戏数据

            self.game_over = True

    def compute_player_utility(self):
        # 如果地主获胜（地主的手牌数量为零）
        if len(self.info_sets['landlord'].player_hand_cards) == 0:
            self.player_utility_dict = {'landlord': 2, 'farmer': -1}    # 地主的效用值为 2，农民的效用值为 -1
        else:
            self.player_utility_dict = {'landlord': -2, 'farmer': 1}    # 地主的效用值为 -2，农民的效用值为 1

    def update_num_wins_scores(self):
        for pos, utility in self.player_utility_dict.items():
            # pos 是玩家的角色（landlord 或 farmer）
            # utility 是该玩家的效用值
            base_score = 2 if pos == 'landlord' else 1      # 基础分数（地主 2，农民 1）
            if utility > 0:                                 # utility 大于 0 即该玩家赢了比赛
                self.num_wins[pos] += 1                     # 增加玩家的胜利次数计数
                self.winner = pos                           # 将游戏的胜利者设为当前玩家 pos

                # 根据 基础分数 和 炸弹数量 
                # 计算玩家分数的增加量
                self.num_scores[pos] += base_score * (2 ** self.bomb_num)
            else:
                # 计算玩家分数的减少量
                self.num_scores[pos] -= base_score * (2 ** self.bomb_num)       # 减少量

    def get_winner(self):
        return self.winner

    def get_bomb_num(self):
        return self.bomb_num

    def compare_action(self, action):
        return action[1]

    @staticmethod
    def action_to_str(action):
        if len(action) == 0:
            return "Pass"
        else:
            return "".join([EnvCard2RealCard[card] for card in action])

    def path_to_str(self, path):
        pstr = ""
        for action in path:
            pstr += self.action_to_str(action) + " "
        return pstr

    @staticmethod
    def have_bomb(cards):
        if 20 in cards and 30 in cards:
            return True
        for i in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 17]:
            if cards.count(i) == 4:
                return True
        return False

    def step(self, position, action=None, update=True):
        if action is not None and len(action) > 0:
            action_list = [[action, 0]]
            win_rate = 0
        else:
            action = []
            win_rate = 0
            action_list = []

            # 如果当前轮到的玩家是指定的 position
            if self.acting_player_position == position:
                # 根据游戏信息集合调用玩家的动作方法，获取动作和动作的置信度
                action, actions_confidence, action_list = self.players[1].act(self.game_infoset)
                win_rate = actions_confidence

                # 特殊情况处理：直接出完牌
                if len(action) != len(self.game_infoset.player_hand_cards):
                    if len(action_list) > 0:
                        for l_action, l_score in action_list:
                            if len(l_action) == len(self.game_infoset.player_hand_cards):
                                m_type = md.get_move_type(l_action)
                                if m_type["type"] not in [md.TYPE_14_4_22, md.TYPE_13_4_2]:
                                    action = l_action
                                    win_rate = 10000
                                    print("env log: 检测到可直接出完")
                                    print()

                # 获取最后两次出牌动作
                last_two_moves = self.get_last_two_moves()
                rival_move = None
                if last_two_moves[0]:
                    rival_move = last_two_moves[0]      # 优先选择第一个动作作为对手的动作
                elif last_two_moves[1]:
                    rival_move = last_two_moves[1]      # 如果第一个动作不存在，则选择第二个动作作为对手的动作

                # 如果不能直接出完牌，则进行路径搜索
                if win_rate != 10000:
                    path_list = []      # 所有可能的出牌路径
                    search_actions(self.game_infoset.player_hand_cards,
                                   self.game_infoset.other_hand_cards,
                                   path_list,
                                   rival_move=rival_move)
                    
                    if len(path_list) > 0:
                        path = select_optimal_path(path_list)       # 选择最优路径
                        if not check_42(path):                      # 检查是否是4带2
                            if action != path[0]:
                                print(f"env log: 检测到可直接出完路径：{self.action_to_str(action)} -> {self.path_to_str(path)}")
                                print()
                                action = path[0]
                                win_rate = 20000

        if update:
            # 设置最后行动玩家为当前行动玩家
            if len(action) > 0:
                self.last_pid = self.acting_player_position

            # 如果动作是炸弹，则增加炸弹数量
            if action in Bombs:
                self.bomb_num += 1

            self.last_move_dict[self.acting_player_position] = action.copy()    # 更新最后一次动作字典
            self.card_play_action_seq.append((position, action))                # 添加动作到出牌序列
            
            self.update_acting_player_hand_cards(action)                        # 更新当前行动玩家的手牌
            
            self.played_cards[self.acting_player_position] += action            # 更新已经出过的牌

            # 如果当前行动玩家是地主，并且出牌不为空，并且还有地主三张底牌未被出过
            if self.acting_player_position == 'landlord' and len(action) > 0 and len(self.three_landlord_cards) > 0:
                # 更新 three_landlord_cards
                for card in action:
                    if len(self.three_landlord_cards) > 0:
                        if card in self.three_landlord_cards:
                            self.three_landlord_cards.remove(card)
                    else:
                        break
            
            # 检查游戏是否结束
            self.check_if_game_overed()

            # 如果游戏还没结束，更新当前行动玩家和游戏信息集合
            if not self.game_over:
                # print(f"env log: 上一次行动玩家是 {self.acting_player_position}")
                # print()
                self.get_acting_player_position()
                # print(f"env log: 当前行动玩家是 {self.acting_player_position}（更新后）")
                # print()
                self.game_infoset = self.get_infoset()

        # 按照置信度排序
        action_list.sort(key=self.compare_action, reverse=True)

        # 根据特定规则进一步调整动作选择
        if len(action_list) >= 2:
            # 检查 第一个动作（优先级最高的动作）的胜率 是否小于 0
            # 如果胜率小于 0，则执行下面的逻辑
            if float(action_list[0][1]) < 0:
                action_list.sort(key=self.compare_action, reverse=True)

                # 选择第二优先级的动作
                action, actions_confidence = action_list[1][0], action_list[1][1]
                win_rate = actions_confidence

            # 如果 action 为空
            if not action:
                # 检查 第二优先级动作 的胜率（乘以 8）是否大于 1
                if float(action_list[1][1]) * 8 > 1:
                    action_list.sort(key=self.compare_action, reverse=True)

                    # 选择第二优先级的动作（第二选择的胜率大于1，直接出）
                    action, actions_confidence = action_list[1][0], action_list[1][1]
                    win_rate = actions_confidence
                
                # 检查以下条件是否成立：
                # - position 是否为 "landlord"
                # - 第一优先级动作 和 第二优先级动作 的胜率差异（乘以 8）是否小于 0.2
                # - 第二优先级动作 的胜率（乘以 8）是否大于 0
                if (position == "landlord" and (float(action_list[0][1]) - float(action_list[1][1])) * 8 < 0.2 and float(action_list[1][1]) * 8 > 0):
                    action_list.sort(key=self.compare_action, reverse=True)
                    
                    # 选择第二优先级的动作（地主第二选择胜率大于0，且与第一选择相差小于0.2，直接出）
                    action, actions_confidence = action_list[1][0], action_list[1][1]
                    win_rate = actions_confidence

        # 构建返回的信息
        action_message = {
            "action": str(''.join([EnvCard2RealCard[c] for c in action])),
            "win_rate": float(win_rate) * 8
        }
        
        def format_action(action_info):
            action_str = ''.join([EnvCard2RealCard[c] for c in action_info[0]])
            return action_str if action_str else "Pass"

        def round_confidence(confidence):
            return str(round(float(confidence) * 8, 3))

        show_action_list = []
        for action_info in action_list:
            action_str = format_action(action_info)
            confidence_str = round_confidence(action_info[1])
            show_action_list.append((action_str, confidence_str))

        return action_message, show_action_list

    # 获取最后一次有效动作
    def get_last_move(self):
        last_move = []
        if len(self.card_play_action_seq) != 0:
            if len(self.card_play_action_seq[-1][1]) == 0:      # 如果最后一个动作的牌列表为空（可能是 pass 动作）
                last_move = self.card_play_action_seq[-2][1]    # 则取倒数第二个动作的牌列表
            else:
                last_move = self.card_play_action_seq[-1][1]    # 否则，取最后一个动作的牌列表
        return last_move

    # 获取最近两次有效动作
    def get_last_two_moves(self):
        last_two_moves = [[], []]
        for card in self.card_play_action_seq[-2:]:
            last_two_moves.insert(0, card[1])
            last_two_moves = last_two_moves[:2]
        return last_two_moves

    # 获取下一个出牌玩家的位置
    def get_acting_player_position(self):
        if self.acting_player_position is None:                     # 如果 self.acting_player_position 是空，则将其设置为 landlord
            self.acting_player_position = 'landlord'                # 表示游戏的初始出牌玩家是：地主
        else:
            if self.acting_player_position == 'landlord':           # 如果 当前出牌玩家 是地主，则将其设置为 landlord_down
                self.acting_player_position = 'landlord_down'       # 表示下一个出牌玩家是：地主的下家

            elif self.acting_player_position == 'landlord_down':    # 如果 当前出牌玩家是 地主的下家，则将其设置为 landlord_up
                self.acting_player_position = 'landlord_up'         # 表示下一个出牌玩家是：地主的上家

            else:
                self.acting_player_position = 'landlord'            # 如果 当前出牌玩家 既不是地主 也不是地主的下家（即当前是地主的上家）
                                                                    # 则将其设置回 landlord，表示下一个出牌玩家：重新回到地主
        return self.acting_player_position

    # 更新当前出牌玩家的手牌信息
    def update_acting_player_hand_cards(self, action):
        if action != []:
            # 更新玩家手牌，删除对应的牌
            if self.acting_player_position == self.players[0]:
                # print("env log: 已更新当前玩家（我的）手牌")
                # print()
                for card in action:
                    self.info_sets[self.acting_player_position].player_hand_cards.remove(card)
            else:
                # print("env log: 已更新另外两个玩家手牌（删除相同数量的牌）")
                # print()
                del self.info_sets[self.acting_player_position].player_hand_cards[0:len(action)]

            self.info_sets[self.acting_player_position].player_hand_cards.sort()

    # 获取当前玩家可以合法出牌的所有可能动作
    def get_legal_card_play_actions(self):
        mg = MovesGener(
            self.info_sets[self.acting_player_position].player_hand_cards)

        action_sequence = self.card_play_action_seq                             # 当前牌局的出牌序列

        rival_move = []
        if len(action_sequence) != 0:
            if len(action_sequence[-1][1]) == 0:                                # 如果最后一次出牌是 Pass（即没有出牌）
                rival_move = action_sequence[-2][1]                             # 则将倒数第二次出牌作为对手的出牌
            else:
                rival_move = action_sequence[-1][1]                             # 否则，将最后一次出牌作为对手的出牌

        # 获取对手出牌的类型和长度
        rival_type = md.get_move_type(rival_move)                               # 根据对手的出牌信息获取出牌类型
        rival_move_type = rival_type['type']                                    # 获取对手出牌的类型
        rival_move_len = rival_type.get('len', 1)                               # 获取对手出牌的长度，如果长度信息不存在，则默认为 1
        
        moves = list()                                                          # 用于存储合法的可能出牌动作

        if rival_move_type == md.TYPE_0_PASS:
            moves = mg.gen_moves()

        elif rival_move_type == md.TYPE_1_SINGLE:
            all_moves = mg.gen_type_1_single()
            moves = ms.filter_type_1_single(all_moves, rival_move)

        elif rival_move_type == md.TYPE_2_PAIR:
            all_moves = mg.gen_type_2_pair()
            moves = ms.filter_type_2_pair(all_moves, rival_move)

        elif rival_move_type == md.TYPE_3_TRIPLE:
            all_moves = mg.gen_type_3_triple()
            moves = ms.filter_type_3_triple(all_moves, rival_move)

        elif rival_move_type == md.TYPE_4_BOMB:
            all_moves = mg.gen_type_4_bomb() + mg.gen_type_5_king_bomb()
            moves = ms.filter_type_4_bomb(all_moves, rival_move)

        elif rival_move_type == md.TYPE_5_KING_BOMB:
            moves = []

        elif rival_move_type == md.TYPE_6_3_1:
            all_moves = mg.gen_type_6_3_1()
            moves = ms.filter_type_6_3_1(all_moves, rival_move)

        elif rival_move_type == md.TYPE_7_3_2:
            all_moves = mg.gen_type_7_3_2()
            moves = ms.filter_type_7_3_2(all_moves, rival_move)

        elif rival_move_type == md.TYPE_8_SERIAL_SINGLE:
            all_moves = mg.gen_type_8_serial_single(repeat_num=rival_move_len)
            moves = ms.filter_type_8_serial_single(all_moves, rival_move)

        elif rival_move_type == md.TYPE_9_SERIAL_PAIR:
            all_moves = mg.gen_type_9_serial_pair(repeat_num=rival_move_len)
            moves = ms.filter_type_9_serial_pair(all_moves, rival_move)

        elif rival_move_type == md.TYPE_10_SERIAL_TRIPLE:
            all_moves = mg.gen_type_10_serial_triple(repeat_num=rival_move_len)
            moves = ms.filter_type_10_serial_triple(all_moves, rival_move)

        elif rival_move_type == md.TYPE_11_SERIAL_3_1:
            all_moves = mg.gen_type_11_serial_3_1(repeat_num=rival_move_len)
            moves = ms.filter_type_11_serial_3_1(all_moves, rival_move)

        elif rival_move_type == md.TYPE_12_SERIAL_3_2:
            all_moves = mg.gen_type_12_serial_3_2(repeat_num=rival_move_len)
            moves = ms.filter_type_12_serial_3_2(all_moves, rival_move)

        elif rival_move_type == md.TYPE_13_4_2:
            all_moves = mg.gen_type_13_4_2()
            moves = ms.filter_type_13_4_2(all_moves, rival_move)

        elif rival_move_type == md.TYPE_14_4_22:
            all_moves = mg.gen_type_14_4_22()
            moves = ms.filter_type_14_4_22(all_moves, rival_move)

        if rival_move_type not in [md.TYPE_0_PASS,
                                   md.TYPE_4_BOMB, md.TYPE_5_KING_BOMB]:
            moves = moves + mg.gen_type_4_bomb() + mg.gen_type_5_king_bomb()

        if len(rival_move) != 0:  # rival_move is not 'pass'
            moves = moves + [[]]

        for m in moves:
            m.sort()

        return moves

    def reset(self):
        self.card_play_action_seq = []
        self.three_landlord_cards = None
        self.game_over = False
        self.acting_player_position = None
        self.player_utility_dict = None
        self.last_move_dict = {'landlord': [], 'landlord_up': [], 'landlord_down': []}
        self.played_cards = {'landlord': [], 'landlord_up': [], 'landlord_down': []}
        self.last_move = []
        self.last_two_moves = []
        self.info_sets = {'landlord': InfoSet('landlord'), 'landlord_up': InfoSet('landlord_up'), 'landlord_down': InfoSet('landlord_down')}
        self.bomb_num = 0
        self.last_pid = 'landlord'
        self.bid_info = [[1, 0.5, 1], [1, 1, 1], [1, 1, -4], [1, 1, 1]]
        self.multiply_info = [1, 1, 1]
        self.bid_count = 0
        self.multiply_count = {'landlord': 0, 'landlord_up': 0, 'landlord_down': 0}
        self.step_count = 0

    # 为当前轮到行动的玩家生成一个信息集合（infoset）
    def get_infoset(self):
        # 设置当前行动玩家的信息集合属性
        self.info_sets[self.acting_player_position].last_pid = self.last_pid
        self.info_sets[self.acting_player_position].legal_actions = self.get_legal_card_play_actions()
        self.info_sets[self.acting_player_position].bomb_num = self.bomb_num
        self.info_sets[self.acting_player_position].last_move = self.get_last_move()
        self.info_sets[self.acting_player_position].last_two_moves = self.get_last_two_moves()
        self.info_sets[self.acting_player_position].last_move_dict = self.last_move_dict

        # 计算其他玩家手牌数量
        self.info_sets[self.acting_player_position].num_cards_left_dict = \
            {pos: len(self.info_sets[pos].player_hand_cards) for pos in ['landlord', 'landlord_up', 'landlord_down']}

        self.info_sets[self.acting_player_position].other_hand_cards = []

        '''
        调整计算其他人手牌的方法，整副牌减去玩家手牌与出过的牌
        for pos in ['landlord', 'landlord_up', 'landlord_down']:
            if pos != self.acting_player_position:
                self.info_sets[
                    self.acting_player_position].other_hand_cards += \
                    self.info_sets[pos].player_hand_cards
        '''

        # 把出过的牌中三个子列表合成一个列表
        played_cards_tmp = []
        for i in list(self.played_cards.values()):
            played_cards_tmp.extend(i)

        # 出过的牌和玩家手上的牌
        played_and_hand_cards = played_cards_tmp + self.info_sets[self.acting_player_position].player_hand_cards

        # 整副牌减去出过的牌和玩家手上的牌，就是其他人的手牌
        for i in set(AllEnvCard):
            self.info_sets[
                self.acting_player_position].other_hand_cards.extend(
                [i] * (AllEnvCard.count(i) - played_and_hand_cards.count(i)))

        # 复制其他信息
        self.info_sets[self.acting_player_position].played_cards = self.played_cards
        self.info_sets[self.acting_player_position].three_landlord_cards = self.three_landlord_cards
        self.info_sets[self.acting_player_position].card_play_action_seq = self.card_play_action_seq
        self.info_sets[self.acting_player_position].all_handcards = \
            {pos: self.info_sets[pos].player_hand_cards for pos in ['landlord', 'landlord_up', 'landlord_down']}

        # 返回当前行动玩家信息集合的深拷贝，确保外部无法直接修改内部状态
        return deepcopy(self.info_sets[self.acting_player_position])


class InfoSet(object):
    """
    The game state is described as infoset, which
    includes all the information in the current situation,
    such as the hand cards of the three players, the
    historical moves, etc.
    """

    def __init__(self, player_position):
        self.player_position = player_position            # 玩家位置，即地主、地主下家或地主上家
        self.player_hand_cards = None                     # 当前玩家的手牌（一个列表）
        self.num_cards_left_dict = None                   # 每个玩家剩余的牌数（一个字典，键是字符串，值是整数）
        self.three_landlord_cards = None                  # 三张地主牌（一个列表）
        self.card_play_action_seq = None                  # 历史出牌记录（一个列表的列表）
        self.other_hand_cards = None                      # 当前玩家其他两个玩家的手牌总和
        self.legal_actions = None                         # 当前出牌的合法动作（一个列表的列表）
        self.last_move = None                             # 最近一次有效出牌
        self.last_two_moves = None                        # 最近两次出牌
        self.last_move_dict = None                        # 所有位置最近一次出牌
        self.played_cards = None                          # 到目前为止出的牌（一个列表）
        self.all_handcards = None                         # 所有玩家的手牌（一个字典）
        self.last_pid = None                              # 最后一个出有效牌的玩家位置，即非"过"的情况
        self.bomb_num = None                              # 到目前为止出的炸弹数

        self.bid_info = [[1, 0.5, 1],
                         [1, 1, 1],
                         [1, 5, -4],
                         [1, 1, 1]]
        if player_position == 'landlord_up':
            self.bid_info = [[1, 0.2, 1],
                             [1, 3.5, 1],
                             [1, 5, 4],
                             [1.035, 1, 0.15]]
        if player_position == 'landlord_down':
            self.bid_info = [[1, 0.2, 1],
                             [1, 3.5, 1],
                             [1, 5, 4],
                             [1.035, 1, 0.15]]

        self.multiply_info = [1, 0.8, 1.3]
        # self.multiply_info = [1, 1, 1]
        # self.multiply_info = [0, 0, 0]
        if player_position == 'landlord_up':
            self.multiply_info = [1, 2.5, 1.3]
        if player_position == 'landlord_down':
            self.multiply_info = [1, 2.5, 1.3]
        
        self.player_id = None
