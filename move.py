class Move:
	"""Class representation of a chess move"""
	def __init__(self, board, start, end, captured_row=None, captured_col=None, primary_move=None, secondary_move=None):
		self.startRow, self.startCol = start
		self.endRow, self.endCol = end
		self.piece_moved = self.get_piece(board, self.startRow, self.startCol)
		self.piece_captured_row = captured_row if captured_row else self.endRow
		self.piece_captured_col = captured_col if captured_col else self.endCol
		self.piece_captured = self.get_piece(board, self.piece_captured_row, self.piece_captured_col)
		self.primary_move = primary_move
		self.secondary_move = secondary_move
		self.move_id = int(f"{self.startRow}{self.startCol}{self.endRow}{self.endCol}")
		# Not true PGN notation, but similar
		self.PGN = self.move_notation()

	def __str__(self):
		return self.PGN

	def __repr__(self):
		return self.PGN

	def __eq__(self, other):
		if isinstance(other, Move):
			return self.move_id == other.move_id

	@staticmethod
	def ranks_to_rows(rank):
		return {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}[rank]

	@staticmethod
	def rows_to_ranks(row):
		return {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}[row]

	@staticmethod
	def files_to_cols(file):
		return {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}[file]

	@staticmethod
	def cols_to_files(col):
		return {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}[col]

	@staticmethod
	def get_piece(board, row, col):
		return board[row][col]

	def get_rank_file(self, row, col):
		return self.cols_to_files(col) + self.rows_to_ranks(row)

	def move_notation(self):
		"""Converts the internal representation of a move to notation similar to PGN"""
		piece = self.piece_moved[1] if self.piece_moved else ""
		return piece + self.get_rank_file(self.endRow, self.endCol)