import chess
import chess.pgn
import svg
import pygame
import io
import math
from lichess import *
from flashcards import *
import os.path

board_size = 500

from_square = None
to_square = None

pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((board_size, board_size))
clock = pygame.time.Clock()

board, best_move = next_problem()

history = []

flipped = not board.turn

incorrect = False
correct_timer = 0
failed = False
review = False

move_sfx = pygame.mixer.Sound(os.path.join('chess_move.wav'))
stats = 1

def render(fill=None, lastmove=None):
    if fill is None:
        fill = dict()
    global pygame_surface
    svg_string = svg.board(
        board=board,
        size=board_size,
        coordinates=False,
        flipped=flipped,
        fill=fill,
        lastmove=lastmove
    )
    pygame_surface = pygame.image.load(io.BytesIO(svg_string.encode()))


def last_move():
    try:
        return board.peek()
    except IndexError:
        return None

pygame_surface = None
render(lastmove=last_move())

def try_move():
    global from_square, to_square, correct_timer, incorrect, failed, review
    try:
        move = board.find_move(from_square, to_square)
        if move == best_move or (board.is_kingside_castling(move) and board.is_kingside_castling(best_move)) or (board.is_queenside_castling(move) and board.is_queenside_castling(best_move)):
            if not failed:
                answer(board, 1)
            board.push(move)
            pygame.mixer.Sound.play(move_sfx)
            render(lastmove=last_move())
            if failed:
                review = True
            else:
                correct_timer = 10
        else:
            if not failed:
                answer(board, 0)
            board.push(move)
            pygame.mixer.Sound.play(move_sfx)
            incorrect = True
            failed = True
            render(fill={to_square: "#c9343080", from_square: "#c9343080"})
        from_square = None
        to_square = None
    except ValueError:
        from_square = to_square
        to_square = None


run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            file, rank = map(lambda a: math.floor(a*8/board_size), pygame.mouse.get_pos())
            pos = rank*8 + (7 - file) if flipped else (7-rank)*8 + file
            if from_square is None:
                from_square = pos
            elif not incorrect and not correct_timer and not review and not history:
                to_square = pos
                try_move()
        if event.type == pygame.MOUSEBUTTONUP:
            file, rank = map(lambda a: math.floor(a * 8 / board_size), pygame.mouse.get_pos())
            pos = rank*8 + (7 - file) if flipped else (7 - rank) * 8 + file
            if history:
                while history:
                    board.push(history.pop())
                pygame.mixer.Sound.play(move_sfx)
                render(lastmove=last_move())
            elif incorrect and from_square is not None:
                board.pop()
                render(lastmove=last_move())
                incorrect = False
                to_square = None
                from_square = None
            elif review and from_square is not None:
                board, best_move = next_problem()
                failed = False
                review = False
                to_square = None
                from_square = None
                flipped = not board.turn
                render(lastmove=last_move())
            elif not incorrect and not correct_timer and not review and from_square and pos != from_square:
                to_square = pos
                try_move()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not review and not correct_timer and not incorrect and not history:
                if not failed:
                    answer(board, 0)
                failed = True
                review = True
                board.push(best_move)
                pygame.mixer.Sound.play(move_sfx)
                render(lastmove=last_move())
                to_square = None
                from_square = None
            if event.key == pygame.K_LEFT and len(board.move_stack) and not incorrect and not correct_timer:
                history.append(board.pop())
                render(lastmove=last_move())
            if event.key == pygame.K_RIGHT and history and not incorrect and not correct_timer:
                board.push(history.pop())
                pygame.mixer.Sound.play(move_sfx)
                render(lastmove=last_move())
            if event.key == pygame.K_ESCAPE:
                run = False

    window.fill((255, 255, 255))
    window.blit(pygame_surface, pygame_surface.get_rect(center=window.get_rect().center))
    if correct_timer:
        correct_timer -= 1
        if not correct_timer:
            board, best_move = next_problem()
            failed = False
            to_square = None
            from_square = None
            flipped = not board.turn
            render(lastmove=last_move())
    pygame.display.flip()


if __name__ == "__main__":
    pass

def save():
    with open(cache_file, 'w') as fp:
        json.dump(cache, fp)
        fp.flush()
    with open(playerdata_file, 'w') as fp:
        json.dump(playerdata, fp)
        fp.flush()

pygame.quit()
save()
exit()