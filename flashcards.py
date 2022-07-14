import ebisu
import json
import time
import chess
import lichess
import chess.pgn
import io
from os.path import exists

def get_json(filename):
    if not exists(filename):
        with open(filename, 'w') as fp:
            json.dump(dict(), fp)
            fp.flush()
    with open(filename) as fp:
        return json.load(fp)

playerdata_file = 'playerdata.json'
playerdata = get_json(playerdata_file)

generator = lichess.position_generator()

total = dict()
success = dict()


def pgn(board):
    return str(chess.pgn.Game.from_board(board))

def from_pgn(pgn):
    pgn_io = io.StringIO(pgn)
    game = chess.pgn.read_game(pgn_io)
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    return board

def next_problem():
    problem_pgn = min(playerdata, key=lambda f: ebisu.predictRecall(tuple(playerdata[f]["ebisu"]), time.time() - playerdata[f]["time"]), default=None)
    if problem_pgn and ebisu.predictRecall(tuple(playerdata[problem_pgn]["ebisu"]), time.time() - playerdata[problem_pgn]["time"], exact=True) < 0.5:
        board = from_pgn(problem_pgn)
        return board, lichess.cloud_eval(board)[0]
    while True:
        board, best_move = next(generator)
        if pgn(board) not in playerdata:
            return board, best_move



def answer(board, correct):
    problem_pgn = pgn(board)
    if problem_pgn not in total:
        total[problem_pgn] = 0
        success[problem_pgn] = 0
    total[problem_pgn] += 1
    success[problem_pgn] += int(correct)

    if problem_pgn in playerdata:
        playerdata[problem_pgn]["ebisu"] = ebisu.updateRecall(tuple(playerdata[problem_pgn]["ebisu"]), success[problem_pgn], total[problem_pgn], time.time() - playerdata[problem_pgn]["time"])
    else:
        playerdata[problem_pgn] = dict()
        playerdata[problem_pgn]["ebisu"] = ebisu.defaultModel(600)
    playerdata[problem_pgn]["time"] = time.time()

