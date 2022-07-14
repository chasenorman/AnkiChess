import requests
import chess
import urllib
import json
import time
import random
import queue
from os.path import exists


override = {}

def get_json(filename):
    if not exists(filename):
        with open(filename, 'w') as fp:
            json.dump(dict(), fp)
            fp.flush()
    with open(filename) as fp:
        return json.load(fp)

cache_file = 'cache.json'
cache = get_json(cache_file)
rate_limit_sleep = 0.3

def explorer(board):
    fen = urllib.parse.quote(board.fen(), safe='')
    if fen not in cache or "explorer" not in cache[fen]:
        time.sleep(rate_limit_sleep)
        request = requests.get(f'https://explorer.lichess.ovh/lichess?variant=standard&speeds=rapid&ratings=1600&topGames=0&recentGames=0&fen={fen}')
        if fen not in cache:
            cache[fen] = dict()
        cache[fen]["explorer"] = json.loads(request.text)
    result = cache[fen]["explorer"]
    total = result["white"] + result["draws"] + result["black"]
    moves = []
    weights = []
    for move in result["moves"]:
        count = move["white"] + move["draws"] + move["black"]
        weights.append(count/total)
        moves.append(chess.Move.from_uci(move["uci"]))
    return moves, weights


def cloud_eval(board):
    fen = urllib.parse.quote(board.fen(), safe='')
    if fen not in cache or "cloud_eval" not in cache[fen]:
        time.sleep(rate_limit_sleep)
        request = requests.get(f'https://lichess.org/api/cloud-eval?fen={fen}')
        if fen not in cache:
            cache[fen] = dict()
        cache[fen]["cloud_eval"] = json.loads(request.text)
    result = cache[fen]["cloud_eval"]
    if "error" in result:
        return None, None
    return chess.Move.from_uci(result["pvs"][0]["moves"].split()[0]), result["pvs"][0]["cp"] / 100


def player_move(board):
    if board.fen() in override:
        return chess.Move.from_uci(override[board.fen()])
    return cloud_eval(board)[0]


def random_position():
    board = chess.Board()
    color = bool(random.getrandbits(1))
    while True:
        if color == board.turn:
            best_move = player_move(board)
            if bool(random.getrandbits(1)):
                return board, best_move
            board.push(best_move)
        else:
            moves, weights = explorer(board)
            board.push(random.choices(moves, weights=weights, k=1)[0])


def position_generator():
    count = 0
    pq = queue.PriorityQueue()
    start = chess.Board()
    pq.put((-1, count, start))
    for move, weight in zip(*explorer(start)):
        count += 1
        board = chess.Board()
        board.push(move)
        pq.put((-weight, count, board))
    while True:
        weight, _, board = pq.get()
        c = board.copy()
        best_move = player_move(board)
        if best_move:
            yield board, best_move
            c.push(best_move)
            for move, probability in zip(*explorer(c)):
                count += 1
                next_board = c.copy()
                next_board.push(move)
                pq.put((probability*weight, count, next_board))