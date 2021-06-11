from math import inf
from time import time
from numpy import array, append, sum


class Node:
    def __init__(self, maximizer):
        self.maximizer = maximizer
        self.children = []
        self.alpha = -inf
        self.beta = inf

    def traverse(self, alpha, beta):
        if len(self.children) == 0:
            if self.maximizer:
                return self.alpha
            else:
                return self.beta

        self.alpha = alpha
        self.beta = beta

        if self.maximizer:
            for node in self.children:
                value = node.traverse(self.alpha, self.beta)
                self.alpha = max(self.alpha, value)

                if self.alpha >= beta:
                    return beta

            return self.alpha

        else:
            for node in self.children:
                value = node.traverse(self.alpha, self.beta)
                self.beta = min(self.beta, value)

                if self.alpha >= self.beta:
                    return alpha

            return self.beta

    def pocket_index(self, value):
        for index, child in enumerate(self.children):
            if child.beta == value:
                return index


def empty_pocket(board, index, steal):
    stones = board[index]
    start = index + 1
    end = index + stones + 1
    board[index] = 0

    if end <= 13:
        board[start:end] += 1
        if steal:
            if end - 1 < 6 and board[end - 1] == 1 and board[13 - end] > 0:
                board[6] += 1 + board[13 - end]
                board[end - 1] = 0
                board[13 - end] = 0
    else:
        board[start: 13] += 1
        stones -= (13 - start)
        while stones > 13:
            board[:13] += 1
            stones -= 13
        board[:stones] += 1

        if steal:
            if stones - 1 < 6 and board[stones - 1] == 1 and board[13 - stones] > 0:
                board[6] += 1 + board[13 - stones]
                board[stones - 1] = 0
                board[13 - stones] = 0

    if sum(board[:6]) == 0:
        board[13] += sum(board[7:13])
        board[7:13] = 0
        return board, True

    elif sum(board[7:13]) == 0:
        board[6] += sum(board[:6])
        board[:6] = 0
        return board, True

    return board, False


def play(board, index, ai, steal):
    if not ai:
        board = append(board[7:], board[:7])

    if ai:
        i = 0
        while i <= index:
            if board[i] == 0:
                index += 1
            i += 1

    board, game_over = empty_pocket(board, index, steal)

    if not ai:
        board = append(board[7:], board[:7])

    return board, game_over


def build_tree(current_board, depth, maximizer, steal):
    root = Node(maximizer)

    if depth > 0:
        if not maximizer:
            current_board = append(current_board[7:], current_board[:7])

        for index in range(6):
            if current_board[index] == 0:
                continue

            board = current_board.copy()
            board, game_over = empty_pocket(board, index, steal)

            if not maximizer:
                board = append(board[7:], board[:7])

            if game_over:
                child = Node(not maximizer)
                if maximizer:
                    child.beta = current_board[6] - current_board[13]
                else:
                    child.alpha = current_board[6] - current_board[13]
                root.children.append(child)

            else:
                root.children.append(build_tree(board, depth - 1, not maximizer, steal))

    else:
        if maximizer:
            root.alpha = current_board[6] - current_board[13]
        else:
            root.beta = current_board[6] - current_board[13]

    return root


def pad(num):
    if num < 10:
        return f' {num}'
    return f'{num}'


def print_board(board):
    player1 = '| |    | '
    player2 = '| |    | '
    for i in range(6):
        player1 += f' | {pad(board[i + 7])} | '
        player2 += f' | {pad(board[5 - i])} | '
    player1 += ' |    | |'
    player2 += ' |    | |'

    print(' ----------------------------------------------------------------')
    print('|  ----    ----    ----    ----    ----    ----    ----    ----  |')
    print(player2)
    print('| |    |   ----    ----    ----    ----    ----    ----   |    | |')
    print(f'| | {pad(board[6])} |                                                  | {pad(board[13])} | |')
    print('| |    |   ----    ----    ----    ----    ----    ----   |    | |')
    print(player1)
    print('|  ----    ----    ----    ----    ----    ----    ----    ----  |')
    print(' ----------------------------------------------------------------')

