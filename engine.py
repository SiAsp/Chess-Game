"""
Stores game state information.
Responsible for determining valid moves in a state.
Keeps move-logs
"""

import numpy as np

# Local imports
from move import Move

class GameState():
	"""Class representing the state of a Chess game."""
	def __init__(self):
		self.board = np.array([
			["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
			["bP" for _ in range(8)],
			["" for _ in range(8)],
			["" for _ in range(8)],
			["" for _ in range(8)],
			["" for _ in range(8)],
			["wP" for _ in range(8)],
			["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
		])
		self.white_move = True
		self.movelog = []
		self.checkmate = False
		self.stalemate = False
		self.white_king_loc = (7, 4)
		self.black_king_loc = (0, 4)

	def make_move(self, move: Move, log=True):
		"""Takes a move-object and executes the move"""
		self.board[move.startRow][move.startCol] = ""		
		self.board[move.piece_captured_row][move.piece_captured_col] = ""
		self.board[move.endRow][move.endCol] = move.piece_moved
		if log:
			self.movelog.append(move)
		if move.piece_moved == "wK":
			self.white_king_loc = (move.endRow, move.endCol)
		if move.piece_moved == "bK":
			self.black_king_loc = (move.endRow, move.endCol)
		if hasattr(move, "secondary_move") and isinstance(move.secondary_move, Move):
			self.make_move(move.secondary_move, log=False)
		else:
			self.white_move = not self.white_move

	def undo_move(self):
		"""Reverses last made move"""
		if self.movelog:
			move = self.movelog.pop()
			self.board[move.startRow][move.startCol] = move.piece_moved
			self.board[move.endRow][move.endCol] = ""
			self.board[move.piece_captured_row][move.piece_captured_col] = move.piece_captured if move.piece_captured else ""
			# Executes a secondary move associated with the move, i.e. castling.
			if hasattr(move, "secondary_move") and isinstance(move.secondary_move, Move):
				move = move.secondary_move
				self.board[move.startRow][move.startCol] = move.piece_moved
				self.board[move.endRow][move.endCol] = ""
				self.board[move.piece_captured_row][move.piece_captured_col] = move.piece_captured if move.piece_captured else ""
			self.white_move = not self.white_move

	def square_attacked(self, row, col):
		"""Check whether a square is attacked or not. Does this by checking all possible opponent-moves in a gamestate."""
		self.white_move = not self.white_move
		possible_moves = self.get_possible_moves()
		self.white_move = not self.white_move
		return any(move.endRow == row and move.endCol == col for move in possible_moves)

	def in_check(self):
		"""Checks whether current player is in check"""
		if self.white_move:
			return self.square_attacked(*self.white_king_loc)
		else:
			return self.square_attacked(*self.black_king_loc)

	def check_game_state(self, moves):
		"""Checks the gamestate for stalemate or checkmate"""
		if not moves:
			if self.in_check:
				self.checkmate = True
			else:
				self.stalemate = True

	def get_valid_moves(self):
		"""
		Generates all valid moves. Takes checks on current player into account.
		This is a fairly rudimentary solution, which might be to slow for implementing ML, we'll find out :)
		"""
		possible_moves = self.get_possible_moves()
		moves = self.remove_selfchecks(possible_moves)
		self.check_game_state(moves)
		return moves

	def remove_selfchecks(self, moves):
		"""Removes moves that put yourself in check"""
		for move in moves.copy():
			self.make_move(move)
			# Swap to opponent to check if in check
			self.white_move = not self.white_move
			if self.in_check():
				moves.remove(move)
			self.white_move = not self.white_move
			self.undo_move()
		return moves

	def get_possible_moves(self):
		"""Generates all possible moves"""
		moves = []
		turn = "w" if self.white_move else "b"
		for row_no, row in enumerate(self.board):
			for col_no, player_piece in enumerate(row):
				if player_piece.startswith(turn):
					piece = player_piece[1]
					if piece == "P":
						self.get_pawn_moves(moves, row_no, col_no)
						self.get_en_passant(moves, row_no, col_no)
					elif piece == "K":
						self.get_king_moves(moves, row_no, col_no)
						self.get_castles(moves)
					elif piece == "Q":
						self.get_queen_moves(moves, row_no, col_no)
					elif piece == "R":
						self.get_rook_moves(moves, row_no, col_no)
					elif piece == "N":
						self.get_knight_moves(moves, row_no, col_no)
					elif piece == "B":
						self.get_bishop_moves(moves, row_no, col_no)
		return moves

	"""
	Methods for moving pieces
	"""

	def get_pawn_moves(self, moves, row_no, col_no):
		"""Appends all possible pawn moves to move-list"""
		if self.white_move:
			# One square forward
			# Check that square ahead is empty
			if 0 <= row_no - 1 < 8 and not self.board[row_no - 1][col_no]:
				moves.append(Move(self.board, (row_no, col_no), (row_no - 1, col_no)))
				# Two squares on first move
				if row_no == 6 and not self.board[row_no - 2][col_no]:
					moves.append(Move(self.board, (row_no, col_no), (row_no - 2, col_no)))
			# Take one move diagonally forward
			if 0 <= row_no - 1 < 8 and 0 <= col_no - 1 < 8 and self.board[row_no - 1][col_no - 1]:
				moves.append(Move(self.board, (row_no, col_no), (row_no - 1, col_no - 1)))
			if 0 <= row_no - 1 < 8 and col_no + 1 < 8 and self.board[row_no - 1][col_no + 1]:
				moves.append(Move(self.board, (row_no, col_no), (row_no - 1, col_no + 1)))
		else:
			# One square forward
			# Check that square ahead is empty
			if 0 <= row_no + 1 < 8 and not self.board[row_no + 1][col_no]:
				moves.append(Move(self.board, (row_no, col_no), (row_no + 1, col_no)))
				# Two squares on first move
				if row_no == 1 and not self.board[row_no + 2][col_no]:
					moves.append(Move(self.board, (row_no, col_no), (row_no + 2, col_no)))
			# Take one move diagonally forward
			if 0 <= row_no + 1 < 8 and 0 <= col_no - 1 < 8 and self.board[row_no + 1][col_no - 1]:
				moves.append(Move(self.board, (row_no, col_no), (row_no + 1, col_no - 1)))
			if 0 <= row_no + 1 < 8 and col_no + 1 < 8 and self.board[row_no + 1][col_no + 1]:
				moves.append(Move(self.board, (row_no, col_no), (row_no + 1, col_no + 1)))
		return moves

	def get_en_passant(self, moves, row_no, col_no):
		col_right = col_no + 1
		col_left = col_no - 1
		if self.movelog:
			last_move = self.movelog[-1]
			if last_move.piece_moved[1] == "P": # index 1 for piecetype, not colour
				if self.white_move:
					if row_no == 3: # Check location of pawn to be moved
						if last_move.startRow == 1 and last_move.endRow == 3: # Check start en end of last move
							if last_move.endCol == col_right:
								moves.append(
									Move(self.board, (row_no, col_no), (row_no - 1, col_right), captured_row=last_move.endRow, captured_col=last_move.endCol)
								)
							elif last_move.endCol == col_left:
								moves.append(
									Move(self.board, (row_no, col_no), (row_no - 1, col_left), captured_row=last_move.endRow, captured_col=last_move.endCol)
								)
				else: # Black move
					if row_no == 5: 
						if last_move.startRow == 1 and last_move.endRow == 5:
							if last_move.endCol == col_right:
								moves.append(
									Move(self.board, (row_no, col_no), (row_no + 1, col_right), captured_row=last_move.endRow, captured_col=last_move.endCol)
								)
							elif last_move.endCol == col_left:
								moves.append(
									Move(self.board, (row_no, col_no), (row_no + 1, col_left), captured_row=last_move.endRow, captured_col=last_move.endCol)
								)
		return moves

	def get_king_moves(self, moves, row_no, col_no):
		"""Appends all possible king moves to move-list"""
		ally_colour = "w" if self.white_move else "b"
		for i in range(-1, 2):
			for j in range(-1, 2):
				if 0 <= row_no + i < 8 and 0 <= col_no + j < 8:
					endpiece = self.board[row_no + i][col_no + j]
					if not endpiece.startswith(ally_colour):
						moves.append(Move(self.board, (row_no, col_no), (row_no + i, col_no + j)))
		return moves

	def get_queen_moves(self, moves, row_no, col_no):
		"""Appends all possible queen moves to move-list"""
		moves.extend(self.get_rook_moves(moves, row_no, col_no))
		moves.extend(self.get_bishop_moves(moves, row_no, col_no))
		return moves

	def get_rook_moves(self, moves, row_no, col_no):
		"""Appends all possible rook moves to move-list"""
		ally_colour = "w" if self.white_move else "b"
		# The dimensions of all possible rook moves
		directs = ((-1, 0), (0, -1), (1, 0), (0, 1))
		# Forwards and backwards
		for d in directs:
			for i in range(1, 8):
				end_row = row_no + d[0] * i 
				end_col = col_no + d[1] * i
				if 0 <= end_row < 8 and 0 <= end_col < 8:
					endpiece = self.board[end_row][end_col]
					if not endpiece.startswith(ally_colour):
						moves.append(Move(self.board, (row_no, col_no), (end_row, end_col)))
					if endpiece:
						break
		return moves

	def get_bishop_moves(self, moves, row_no, col_no):
		"""Appends all possible bishop moves to move-list"""
		ally_colour = "w" if self.white_move else "b"
		# The dimensions of all possible bishop moves
		directs = ((-1, -1), (1, 1), (-1, 1), (1, -1))
		for d in directs:
			for i in range(1, 8):
				end_row = row_no + d[0] * i 
				end_col = col_no + d[1] * i
				if 0 <= end_row < 8 and 0 <= end_col < 8:
					endpiece = self.board[end_row][end_col]
					if not endpiece.startswith(ally_colour):
						moves.append(Move(self.board, (row_no, col_no), (end_row, end_col)))
					if endpiece:
						break
		return moves

	def get_knight_moves(self, moves, row_no, col_no):
		"""Appends all possible knight moves to move-list"""
		ally_colour = "w" if self.white_move else "b"
		# All distances from current square to possible squares
		possible_moves = [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]
		for move in possible_moves:
			end_row = row_no + move[0] 
			end_col = col_no + move[1]
			if 0 <= end_row < 8 and 0 <= end_col < 8:
				endpiece = self.board[end_row][end_col]
				if not endpiece.startswith(ally_colour):
					moves.append(Move(self.board, (row_no, col_no), (end_row, end_col)))
		return moves

	def get_castles(self, moves):
		if self.white_move:
			# check king has not moved
			if not any((move.startRow, move.startCol) == (7, 4) for move in self.movelog):
				# Checking that Rh1 has not moved
				if not any((move.startRow, move.startCol) == (7, 7) for move in self.movelog) and not any([self.board[7][5] != "", self.board[7][6] != ""]):
					rook_move = Move(self.board, (7, 7), (7, 5))
					king_move = Move(self.board, (7, 4), (7, 6), secondary_move=rook_move)
					king_move.PGN = "O-O"
					moves.append(king_move)
				# Checking that Ra1 has not moved
				if not any((move.startRow, move.startCol) == (7, 0) for move in self.movelog) and not any([self.board[7][1] != "", self.board[7][2] != "", self.board[7][3] != ""]):
					print(21980371)
					rook_move = Move(self.board, (7, 0), (7, 3))
					king_move = Move(self.board, (7, 4), (7, 2), secondary_move=rook_move)
					king_move.PGN = "O-O-O"
					moves.append(king_move)
		else:
			if not any((move.startRow, move.startCol) == (0, 4) for move in self.movelog):
				if not any((move.startRow, move.startCol) == (0, 7) for move in self.movelog) and not any([self.board[0][5] != "", self.board[0][6] != ""]):
					rook_move = Move(self.board, (0, 7), (0, 5))
					king_move = Move(self.board, (0, 4), (0, 6), secondary_move=rook_move)
					king_move.PGN = "O-O"
					moves.append(king_move)
				if not any((move.startRow, move.startCol) == (0, 0) for move in self.movelog) and not any([self.board[0][1] != "", self.board[0][2] != "", self.board[0][3] != ""]):
					rook_move = Move(self.board, (0, 0), (0, 3))
					king_move = Move(self.board, (0, 4), (0, 2), secondary_move=rook_move)
					king_move.PGN = "O-O-O"
					moves.append(king_move)
		return moves