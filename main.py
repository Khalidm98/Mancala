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


if __name__ == '__main__':
    load, save, first, steal, difficulty = '', '', '', '', ''
    while not (load in ['y', 'Y', 'n', 'N']):
        load = input('Do you want to load previous game? (Y/N): ')

    if load in ['y', 'Y']:
        file = open('progress.txt')
        loaded = file.read()
        difficulty = int(loaded[-1])
        loaded = loaded[:-2]

        steal = loaded[-1]
        if steal == '1':
            steal = True
        else:
            steal = False
        loaded = loaded[:-2]

        board = array([])
        for pocket in loaded.split():
            board = append(board, [int(pocket)])
        board = board.astype(int)
        print_board(board)
        print()
        file.close()

    else:
        while not (first in ['y', 'Y', 'n', 'N']):
            first = input('Do you want to play first? (Y/N): ')
        if first in ['y', 'Y']:
            first = True
        elif first in ['n', 'N']:
            first = False

        while not (steal in ['y', 'Y', 'n', 'N']):
            steal = input('Play with stealing? (Y/N): ')
        if steal in ['y', 'Y']:
            steal = True
        elif steal in ['n', 'N']:
            steal = False

        while not (difficulty in ['e', 'E', 'm', 'M', 'h', 'H']):
            difficulty = input('Select difficulty: (Easy - E), (Medium - M), (Hard - H): ')
        if difficulty in ['e', 'E']:
            difficulty = 4
        elif difficulty in ['m', 'M']:
            difficulty = 6
        elif difficulty in ['h', 'H']:
            difficulty = 8

        board = array([4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0])
        print_board(board)
        print()

        if not first:
            print('AI is thinking...')
            root = build_tree(board, difficulty, True, steal)
            best_move = root.traverse(-inf, inf)
            index = root.pocket_index(best_move)
            board = play(board, index, True, steal)[0]
            print_board(board)
            print()

    while True:
        index = ''
        while not (index in ['0', '1', '2', '3', '4', '5', 'q', 'Q']):
            index = input('Select a pocket to play [0-5] or (Q) for quit: ')

        if index == 'q' or index == 'Q':
            while not (save in ['y', 'Y', 'n', 'N']):
                save = input('Do you want to save? (Y/N): ')

            if save in ['y', 'Y']:
                pockets = ''
                for pocket in board:
                    pockets += str(pocket) + ' '

                if steal:
                    pockets += '1 '
                else:
                    pockets += '0 '
                pockets += str(difficulty)

                file = open('progress.txt', 'w')
                file.write(pockets)
                file.close()
                print('Saved successfully.')
            break

        index = int(index)
        if board[index + 7] == 0:
            print('You cannot play an empty pocket!')
            continue

        board, game_over = play(board, index, False, steal)
        print_board(board)
        print()
        if game_over:
            if board[6] > board[13]:
                print('AI WINS')
            elif board[6] < board[13]:
                print('YOU WIN')
            else:
                print('DEAL')
            break

        t1 = time()
        print('AI is thinking...')
        root = build_tree(board, difficulty, True, steal)
        best_move = root.traverse(-inf, inf)
        index = root.pocket_index(best_move)
        board, game_over = play(board, index, True, steal)
        print_board(board)
        t2 = time()
        print(f'{t2 - t1} sec')
        print()
        if game_over:
            if board[6] > board[13]:
                print('AI WINS')
            elif board[6] < board[13]:
                print('YOU WIN')
            else:
                print('DEAL')
            break

    if not (save in ['n', 'N']):
        input('Enter any key to exit\n')
