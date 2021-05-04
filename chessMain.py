"""
Main driver col.
Handles user input and displays game state.
"""

# Imports
import pygame
from loguru import logger

# Local imports
from engine import GameState
from move import Move

WIDTH = HEIGHT = 512
DIMENSION = 8

SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
	"""
	Loads all piece images into a dict.
	Format {piece_name: piece_image}
	"""
	pieces = ["bP", "bR", "bN", "bB", "bQ", "bK", "wP", "wR", "wN", "wB", "wQ", "wK"]
	for piece in pieces:
		IMAGES[piece] = pygame.transform.scale(pygame.image.load(f"pieces/{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))


def draw_board(screen):
	"""
	Responsible for drawing the board.
	"""
	WHITE, BLACK = (235, 235, 208), (119, 148, 85)
	for row_no in range(DIMENSION):
		for col_no in range(DIMENSION):
			is_white = (row_no + col_no) % 2 == 0
			square_colour = WHITE if is_white else BLACK
			pygame.draw.rect(screen, square_colour, pygame.Rect(col_no*SQUARE_SIZE, row_no*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
	"""
	Responsible for drawing the pieces on the board from current game state.
	"""
	for row_no in range(DIMENSION):
		for col_no in range(DIMENSION):
			piece = board[row_no][col_no]
			if piece:
				screen.blit(IMAGES[piece], pygame.Rect(col_no*SQUARE_SIZE, row_no*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_game_state(screen, gs):
	"""
	Responsible for all graphics within a game state.
	"""
	draw_board(screen)
	draw_pieces(screen, gs.board)


def main():
	"""
	Main gameloop driver.
	"""
	logger.info("Starting game")
	pygame.init()

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	screen.fill(pygame.Color("white"))
	gs = GameState()
	load_images()

	running = True
	# Flag for when a move is made, triggers get_valid_moves-call
	move_made = False
	valid_moves = gs.get_valid_moves()
	# Keeps track og last clicked square: (x, y)
	selected_square = ()
	# Keeps track of player clicks: [(x, y), (x, y)]
	player_clicks = []
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				logger.info("Exiting")
				running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
				# Same square clicked twice
				if selected_square == (row, col):
					# Undo last clicks
					selected_square = ()
					player_clicks = []
				else:
					selected_square = (row, col)
					player_clicks.append(selected_square)
				if len(player_clicks) == 2:
					move = Move(gs.board, player_clicks[0], player_clicks[1])
					if move in valid_moves:
						move = valid_moves[valid_moves.index(move)]
						gs.make_move(move)
						move_made = True
						selected_square = ()
						player_clicks = []
						logger.success(f"Move: {move.PGN}")
					else:
						logger.error(f"{move.move_notation()} - Not a valid move")
						player_clicks = [selected_square]
			elif event.type == pygame.KEYDOWN:
				# Undo move on left arrow-key
				if event.key == pygame.K_LEFT:
					gs.undo_move()
					# As valid_moves has been refreshed with the last move, undoing it needs to generate a new move-list again
					move_made = True

		if move_made:
			valid_moves = gs.get_valid_moves()
			move_made = False
		if gs.stalemate or gs.checkmate:
			running = False
			if gs.stalemate:
				logger.info("Stalemate")
			if gs.checkmate:
				logger.info("Mate!")

		draw_game_state(screen, gs)
		clock.tick(MAX_FPS)
		pygame.display.flip()

if __name__ == '__main__':
	main()
