import chess
import svg
import pygame
import io
import math
from lichess import *

board_size = 500


from_square = None
to_square = None

pygame.init()
window = pygame.display.set_mode((board_size, board_size))
clock = pygame.time.Clock()


board_generator = position_generator()

board, best_move = next(board_generator)
flipped = not board.turn

incorrect = False
correct_timer = 0

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
    global from_square, to_square, correct_timer, incorrect
    try:
        move = board.find_move(from_square, to_square)
        if move == best_move:
            board.push(move)
            #render(fill={to_square: "#acce5980", from_square: "#acce5980"})
            render(lastmove=last_move())
            correct_timer = 10
        else:
            board.push(move)
            incorrect = True
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
            elif not incorrect:
                to_square = pos
                try_move()
        if event.type == pygame.MOUSEBUTTONUP:
            file, rank = map(lambda a: math.floor(a * 8 / board_size), pygame.mouse.get_pos())
            pos = rank*8 + (7 - file) if flipped else (7 - rank) * 8 + file
            if incorrect and from_square is not None:
                board.pop()
                render(lastmove=last_move())
                incorrect = False
            elif from_square and pos != from_square:
                to_square = pos
                try_move()


    window.fill((255, 255, 255))
    window.blit(pygame_surface, pygame_surface.get_rect(center=window.get_rect().center))
    if correct_timer:
        correct_timer -= 1
        if not correct_timer:
            board, best_move = next(board_generator)
            to_square = None
            from_square = None
            flipped = not board.turn
            render(lastmove=last_move())
    pygame.display.flip()


if __name__ == "__main__":
    pass

pygame.quit()
flush_cache()
exit()