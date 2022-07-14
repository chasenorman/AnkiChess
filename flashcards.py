import ebisu
import json
import time
import chess
import lichess
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


def next_problem():
    problem_fen = min(playerdata, key=lambda f: ebisu.predictRecall(tuple(playerdata[f]["ebisu"]), time.time() - playerdata[f]["time"]), default=None)
    if problem_fen and ebisu.predictRecall(tuple(playerdata[problem_fen]["ebisu"]), time.time() - playerdata[problem_fen]["time"], exact=True) < 0.5:
        board = chess.Board(problem_fen)
        return board, lichess.cloud_eval(board)[0]
    while True:
        board, best_move = next(generator)
        if board.fen() not in playerdata:
            return board, best_move



def answer(board, correct):
    fen = board.fen()
    if fen not in total:
        total[fen] = 0
        success[fen] = 0
    total[fen] += 1
    success[fen] += int(correct)

    if fen in playerdata:
        playerdata[fen]["ebisu"] = ebisu.updateRecall(tuple(playerdata[fen]["ebisu"]), success[fen], total[fen], time.time() - playerdata[fen]["time"])
    else:
        playerdata[fen] = dict()
        playerdata[fen]["ebisu"] = ebisu.defaultModel(300)
    playerdata[fen]["time"] = time.time()

