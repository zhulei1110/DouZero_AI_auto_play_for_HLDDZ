import collections
import itertools

from douzero.env.utils import MIN_SINGLE_CARDS, MIN_PAIRS, MIN_TRIPLES, select

class MovesGener(object):
    """
    This is for generating the possible combinations
    """

    def __init__(self, cards_list):
        self.cards_list = cards_list
        self.cards_dict = collections.Counter(self.cards_list)
        # repeats_dict is for storing cards of repeats 1-4
        self.repeats_dict = collections.defaultdict(list)
        for k, v in self.cards_dict.items():
            for i in range(1, v + 1):
                self.repeats_dict[i].append([k] * i)

        self.single_card_moves = self.repeats_dict[1]
        self.pair_moves = self.repeats_dict[2]
        self.triple_cards_moves = self.repeats_dict[3]
        self.bomb_moves = self.repeats_dict[4]
        self.final_bomb_moves = [[30, 20]] if 20 in self.cards_dict and 30 in self.cards_dict else []

    def _gen_serial_moves(self, cards, min_serial, repeat=1, repeat_num=0):
        moves = []
        # d_left is a dictionary which stores the consecutive numbers before it
        d_left = {}
        for card in self.repeats_dict[repeat]:
            card = card[0]
            if card - 1 not in d_left:
                d_left[card] = 1
            else:
                d_left[card] = d_left[card - 1] + 1
                if d_left[card] >= min_serial:
                    for i in range(min_serial - 1, d_left[card]):
                        moves.append([x for x in range(card - i, card + 1) for _ in range(repeat)])
        return moves

    def gen_type_1_single(self):
        return self.single_card_moves

    def gen_type_2_pair(self):
        return self.pair_moves

    def gen_type_3_triple(self):
        return self.triple_cards_moves

    def gen_type_4_bomb(self):
        return self.bomb_moves

    def gen_type_5_king_bomb(self):
        return self.final_bomb_moves

    def gen_type_6_3_1(self):
        result = []
        for t in self.single_card_moves:
            for i in self.triple_cards_moves:
                if t[0] != i[0]:
                    result.append(t + i)
        return result

    def gen_type_7_3_2(self):
        result = list()
        for t in self.pair_moves:
            for i in self.triple_cards_moves:
                if t[0] != i[0]:
                    result.append(t + i)
        return result

    def gen_type_8_serial_single(self, repeat_num=0):
        return self._gen_serial_moves(self.cards_list, MIN_SINGLE_CARDS, repeat=1, repeat_num=repeat_num)

    def gen_type_9_serial_pair(self, repeat_num=0):
        single_pairs = self.pair_moves
        return self._gen_serial_moves(single_pairs, MIN_PAIRS, repeat=2, repeat_num=repeat_num)

    def gen_type_10_serial_triple(self, repeat_num=0):
        single_triples = self.triple_cards_moves
        return self._gen_serial_moves(single_triples, MIN_TRIPLES, repeat=3, repeat_num=repeat_num)

    def gen_type_11_serial_3_1(self, repeat_num=0):
        serial_3_moves = self.triple_cards_moves
        serial_3_1_moves = list()

        for s3 in serial_3_moves:  # s3 is like [3,3,3,4,4,4]
            s3_set = set(s3)
            new_cards = [i for i in self.cards_list if i not in s3_set]

            # Get any s3_len items from cards
            subcards = select(new_cards, len(s3_set))

            for i in subcards:
                serial_3_1_moves.append(s3 + i)

        return list(k for k, _ in itertools.groupby(serial_3_1_moves))

    def gen_type_12_serial_3_2(self, repeat_num=0):
        serial_3_moves = self.triple_cards_moves
        serial_3_2_moves = list()
        pair_set = sorted([k for k, v in self.cards_dict.items() if v >= 2])

        for s3 in serial_3_moves:
            s3_set = set(s3)
            pair_candidates = [i for i in pair_set if i not in s3_set]

            # Get any s3_len items from cards
            subcards = select(pair_candidates, len(s3_set))
            for i in subcards:
                serial_3_2_moves.append(sorted(s3 + i * 2))

        return serial_3_2_moves

    def gen_type_13_4_2(self):
        four_cards = [x[0] for x in self.bomb_moves]
        result = list()
        for fc in four_cards:
            cards_list = [k for k in self.cards_list if k != fc]
            subcards = select(cards_list, 2)
            for i in subcards:
                result.append([fc] * 4 + i)
        return list(k for k, _ in itertools.groupby(result))

    def gen_type_14_4_22(self):
        four_cards = [x[0] for x in self.bomb_moves]

        result = list()
        for fc in four_cards:
            cards_list = [k for k, v in self.cards_dict.items() if k != fc and v >= 2]
            subcards = select(cards_list, 2)
            for i in subcards:
                result.append([fc] * 4 + [i[0], i[0], i[1], i[1]])
        return result

    # generate all possible moves from given cards
    def gen_moves(self):
        moves = []
        moves.extend(self.single_card_moves)
        moves.extend(self.pair_moves)
        moves.extend(self.triple_cards_moves)
        moves.extend(self.bomb_moves)
        moves.extend(self.final_bomb_moves)
        moves.extend(self.gen_type_6_3_1())
        moves.extend(self.gen_type_7_3_2())
        moves.extend(self.gen_type_8_serial_single())
        moves.extend(self.gen_type_9_serial_pair())
        moves.extend(self.gen_type_10_serial_triple())
        moves.extend(self.gen_type_11_serial_3_1())
        moves.extend(self.gen_type_12_serial_3_2())
        moves.extend(self.gen_type_13_4_2())
        moves.extend(self.gen_type_14_4_22())
        return moves

    def gen_moves_by_type(self, mtype):
        if mtype == 1:
            return self.gen_type_1_single()
        elif mtype == 2:
            return self.gen_type_2_pair()
        elif mtype == 3:
            return self.gen_type_3_triple()
        elif mtype == 4:
            return self.gen_type_4_bomb()
        elif mtype == 5:
            return self.gen_type_5_king_bomb()
        elif mtype == 6:
            return self.gen_type_6_3_1()
        elif mtype == 7:
            return self.gen_type_7_3_2()
        elif mtype == 8:
            return self.gen_type_8_serial_single()
        elif mtype == 9:
            return self.gen_type_9_serial_pair()
        elif mtype == 10:
            return self.gen_type_10_serial_triple()
        elif mtype == 11:
            return self.gen_type_11_serial_3_1()
        elif mtype == 12:
            return self.gen_type_12_serial_3_2()
        elif mtype == 13:
            return self.gen_type_13_4_2()
        elif mtype == 14:
            return self.gen_type_14_4_22()
        else:
            return []