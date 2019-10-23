from __future__ import division

import time
from random import choice
from math import log, sqrt

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Board(object):
    def start(self):
        start = (   0, 2, 0, 2, 0, 2, 0, 2,
                    2, 0, 2, 0, 2, 0, 2, 0,
                    0, 2, 0, 2, 0, 2, 0, 2,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    1, 0, 1, 0, 1, 0, 1, 0,
                    0, 1, 0, 1, 0, 1, 0, 1,
                    1, 0, 1, 0, 1, 0, 1, 0, (-1, -1), 1)
        return start

    def current_player(self, state):
        return state[-1]

    def remove_piece(self, state, (x,y)):
        state[8 * x + y] = 0
        return state

    def king(self, state, (x,y)):
        if state[8 * x + y] != 0:
            if (state[8 * x + y] == 2 and x == 7) or (state[8 * x + y] == 1 and x == 0):
                state[8 * x + y] = state[8 * x + y] * (-1)
        return state

    def next_state(self, state, play):
        hop = (-1, -1)
        start_x, start_y, end_x, end_y = play
        player = state[-1]
        state = list(state)
        state[8 * end_x + end_y] = state[8 * start_x + start_y]
        state = self.remove_piece(state, (start_x, start_y))
        state = self.king(state, (end_x, end_y))
        state[-2] = (-1, -1)
        if abs(end_x - start_x) > 1 or abs(end_y - start_y) > 1:
            state = self.remove_piece(state, ((start_x + end_x)//2, (start_y + end_y)//2))
            legal_moves = self.all_legal_moves(tuple(state))
            if legal_moves != []:
                for move in legal_moves:
                    if (move[0] == end_x) and (move[1] == end_y) and (abs(move[2] - end_x) > 1 or abs(move[3] - end_y) > 1):
                        hop = (end_x, end_y)
        state[-2] = hop
        if hop == (-1, -1):
            state[-1] = 3 - player
        return tuple(state)
    
    def rel(self, dir, (x,y)):
		if dir == NORTHWEST:
			return (x, y, x - 1, y - 1)
		elif dir == NORTHEAST:
			return (x, y, x - 1, y + 1)
		elif dir == SOUTHWEST:
			return (x, y, x + 1, y - 1)
		elif dir == SOUTHEAST:
			return (x, y, x + 1, y + 1)
		else:
			return 0

    def blind_legal_moves(self, state, (x,y)):
        hop = state[-2]
        if state[8 * x + y] != 0:
			if hop == (-1, -1) and state[8 * x + y] == 1:
				blind_legal_moves = [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y))]
			elif hop == (-1, -1) and state[8 * x + y] == 2:
				blind_legal_moves = [self.rel(SOUTHWEST, (x,y)), self.rel(SOUTHEAST, (x,y))]
			else:
				blind_legal_moves = [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y)), self.rel(SOUTHWEST, (x,y)), self.rel(SOUTHEAST, (x,y))]
        else:
			blind_legal_moves = []
        return blind_legal_moves

    def on_board(self, (x,y)):
		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True

    def legal_moves(self, state, (x,y)):
        blind_legal_moves = self.blind_legal_moves(state, (x,y))
        legal_moves = []
        hop = state[-2]
        if hop == (-1, -1):
            for move in blind_legal_moves:
                move_x, move_y = move[2], move[3]
                if hop == (-1, -1):
                    if self.on_board((move_x, move_y)):
                        if state[8 * move_x + move_y] == 0:
                            legal_moves.append(move)
                        elif abs(state[8 * move_x + move_y]) != abs(state[8 * x + y]) and self.on_board((move_x + (move_x - x), move_y + (move_y - y))) and state[8 * (move_x + (move_x - x)) + move_y + (move_y - y)] == 0:
                            legal_moves.append((x, y, move_x + (move_x - x), move_y + (move_y - y)))
        else:
            for move in blind_legal_moves:
                move_x, move_y = move[2], move[3]
                if self.on_board((move_x, move_y)) and state[8 * move_x + move_y] != 0:
                    if abs(state[8 * move_x + move_y]) != abs(state[8 * x + y]) and self.on_board((move_x + (move_x - x), move_y + (move_y - y))) and state[8 * (move_x + (move_x - x)) + (move_y + (move_y - y))] == 0:
                        legal_moves.append((x, y, move_x + (move_x - x), move_y + (move_y - y)))
        return legal_moves

    def all_legal_moves(self, state):
        local_moves = []
        legal_moves = []
        capture_moves = []
        player = state[-1]
        hop = state[-2]
        for i in xrange(8):
            for j in xrange(8):
                if abs(state[8 * i + j]) == player:
                    local_moves = self.legal_moves(state, (i, j))
                    if local_moves != []:
                        legal_moves.extend(local_moves)
                        for move in local_moves:
                            if (abs(move[2] - i) > 1 or abs(move[3] - j) > 1):
                                capture_moves.append(move)
        if capture_moves != []:
            if (hop != (-1, -1)):
                legal_moves = []
                for move in capture_moves:
                    if move[0] == hop[0] and move[1] == hop[1]:
                        legal_moves.append(move)
                return legal_moves
            else:
                return capture_moves
        else:
            return legal_moves

    def legal_plays(self, state_history):
        state = state_history[-1]
        return self.all_legal_moves(state)

    def check_for_endgame(self, state):
        if self.all_legal_moves(state) != []:
            return False
        return True

    def winner(self, state_history):
        state = state_history[-1]
        player = state[-1]
        if self.check_for_endgame(state):
            if player == 1:
                return 2
            elif player == 2:
                return 1
        return 0

class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        self.calculation_time = kwargs.get('time', 1)
        self.max_moves = kwargs.get('max_moves', 1000)
        self.C = kwargs.get('C', 1.4)

        self.board = board
        self.states = []
        self.wins = {}
        self.plays = {}
        self.max_depth = 0

    def update(self, state):
        self.states.append(state)

    def get_play(self):
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])
        written_return = {}

        if not legal:
            return
        if len(legal) == 1:
            written_return["simulations"] = 0
            written_return["time"] = "0.00"
            written_return["games"] = [{"move": list(legal[0]), "winrate": "N/A", "wins": 0, "plays": 0}]
            written_return["upfront"] = 0
            return legal[0], written_return

        games = 0
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            self.run_simulation()
            games += 1

        moves_states = [(p, self.board.next_state(state, p)) for p in legal]

        written_return["simulations"] = games
        written_return["time"] = "{0:.2f}".format(time.time() - begin)

        percent_wins, move = max(
            (
                self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
                p
            ) for p, S in moves_states
        )

        written_return["games"] = []
        for x in sorted(
            ((100 * self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
            self.wins.get((player, S), 0),
            self.plays.get((player, S), 0),
            p)
                for p, S in moves_states),
                reverse=True
        ):
            written_return["games"].append({"move": list(x[3]), "winrate": "{0:.2f}".format(x[0]), "wins": x[1], "plays": x[2]})

        written_return["upfront"] = self.max_depth

        return move, written_return

    def run_simulation(self):
        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)

        expand = True
        for t in range(1, self.max_moves + 1):
            legal = self.board.legal_plays(states_copy)
            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get((player, S)) for p, S in moves_states):
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                    self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                move, state = choice(moves_states)

            states_copy.append(state)

            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if (winner):
                break

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if (player == winner):
                wins[(player, state)] += 1