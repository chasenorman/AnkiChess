import requests
import chess
import urllib
import json

cache_file = 'cache.json'
cache = json.load(open(cache_file))

def flush_cache():
    with open(cache_file, 'w') as fp:
        json.dump(cache, fp)

def explorer(board):
    fen = urllib.parse.quote(board.fen(), safe='')
    if fen not in cache or "explorer" not in cache[fen]:
        request = requests.get(f'https://explorer.lichess.ovh/lichess?variant=standard&speeds=rapid&ratings=1600&topGames=0&recentGames=0&fen={fen}')
        if fen not in cache:
            cache[fen] = dict()
        cache[fen]["explorer"] = json.loads(request.text)
    result = cache[fen]["explorer"]
    total = result["white"] + result["draws"] + result["black"]
    e = []
    for move in result["moves"]:
        count = move["white"] + move["draws"] + move["black"]
        e.append((count/total, chess.Move.from_uci(move["uci"])))
    return e


def cloud_eval(board):
    fen = urllib.parse.quote(board.fen(), safe='')
    if fen not in cache or "cloud_eval" not in cache[fen]:
        request = requests.get(f'https://lichess.org/api/cloud-eval?fen={fen}')
        if fen not in cache:
            cache[fen] = dict()
        cache[fen]["cloud_eval"] = json.loads(request.text)
    result = cache[fen]["cloud_eval"]
    if "error" in result:
        return None
    return chess.Move.from_uci(result["pvs"][0]["moves"].split()[0]), result["pvs"][0]["cp"] / 100
