from enum import Enum

RealCards = ['D', 'X', '2', 'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3']

Bombs = [
    [3, 3, 3, 3],
    [4, 4, 4, 4],
    [5, 5, 5, 5],
    [6, 6, 6, 6],
    [7, 7, 7, 7],
    [8, 8, 8, 8],
    [9, 9, 9, 9],
    [10, 10, 10, 10],
    [11, 11, 11, 11],
    [12, 12, 12, 12],
    [13, 13, 13, 13],
    [14, 14, 14, 14],
    [17, 17, 17, 17],
    [30, 20]
]

RealCard2EnvCard = {
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14,
    '2': 17,
    'X': 20,
    'D': 30
}

AllEnvCard = [
    3, 3, 3, 3,
    4, 4, 4, 4,
    5, 5, 5, 5,
    6, 6, 6, 6,
    7, 7, 7, 7,
    8, 8, 8, 8,
    9, 9, 9, 9,
    10, 10, 10, 10,
    11, 11, 11, 11,
    12, 12, 12, 12,
    13, 13, 13, 13,
    14, 14, 14, 14,
    17, 17, 17, 17,
    20, 30
]

EnvCard2RealCard = {
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: 'T',
    11: 'J',
    12: 'Q',
    13: 'K',
    14: 'A',
    17: '2',
    20: 'X',
    30: 'D'
}

EnvCard2IdxMap = {
    3: 0,
    4: 1,
    5: 2,
    6: 3,
    7: 4,
    8: 5,
    9: 6,
    10: 7,
    11: 8,
    12: 9,
    13: 10,
    14: 11,
    17: 12,
    20: 13,
    30: 14
}

RealCard2IdxMap = {
    '3': 0,
    '4': 1,
    '5': 2,
    '6': 3,
    '7': 4,
    '8': 5,
    '9': 6,
    'T': 7,
    'J': 8,
    'Q': 9,
    'K': 10,
    'A': 11,
    '2': 12,
    'X': 13,
    'D': 14
}

class AutomaticModeEnum(Enum):
    FULL = 1
    SEMI = 2
    MANUAL = 3