import chess
import chess.svg
import pygame
import io
import math
from lichess import *

board_size = 500

flipped = False

from_square = None
to_square = None

pygame.init()
window = pygame.display.set_mode((board_size, board_size))
clock = pygame.time.Clock()


board = chess.Board()
cloud_eval(board)

def render():
    global pygame_surface
    svg_string = chess.svg.board(
        board=board,
        size=board_size,
        coordinates=False,
        flipped=flipped
    )
    pygame_surface = pygame.image.load(io.BytesIO(svg_string.encode()))


pygame_surface = None
render()

def try_move():
    global from_square, to_square
    try:
        move = board.find_move(from_square, to_square)
        print(move)
        board.push(move)
        render()
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
            if from_square == None:
                from_square = pos
            else:
                to_square = pos
                try_move()
        if event.type == pygame.MOUSEBUTTONUP:
            file, rank = map(lambda a: math.floor(a * 8 / board_size), pygame.mouse.get_pos())
            pos = rank*8 + (7 - file) if flipped else (7 - rank) * 8 + file
            if from_square and pos != from_square:
                to_square = pos
                try_move()


    window.fill((255, 255, 255))
    window.blit(pygame_surface, pygame_surface.get_rect(center = window.get_rect().center))
    pygame.display.flip()


if __name__ == "__main__":
    pass

pygame.quit()
flush_cache()
exit()