from enum import IntEnum
from typing import Iterable

class CellState(IntEnum):
	UNKNOWN = 0
	EMPTY = 1
	FILLED = 2

UNKNOWN = CellState.UNKNOWN
EMPTY = CellState.EMPTY
FILLED = CellState.FILLED

class NonogramSolver:
	def __init__(
		self,
		row_clues_input: list[list[int]],
		col_clues_input: list[list[int]],
	) -> None:
		self.num_rows = len(row_clues_input)
		self.num_cols = len(col_clues_input)
		self.row_clues = row_clues_input
		self.col_clues = col_clues_input
		self.grid: list[list[CellState]] = [
			[UNKNOWN for _ in range(self.num_cols)] for _ in range(self.num_rows)
		]
		self.row_patterns: list[list[list[CellState]]] = [
			[] for _ in range(self.num_rows)
		]
		self.col_patterns: list[list[list[CellState]]] = [
			[] for _ in range(self.num_cols)
		]
		self.current_row_pattern_indices: list[list[int]] = [
			[] for _ in range(self.num_rows)
		]
		self.current_col_pattern_indices: list[list[int]] = [
			[] for _ in range(self.num_cols)
		]
		self.solutions: list[list[list[CellState]]] = []

		for i in range(self.num_rows):
			self.row_patterns[i] = self.generate_line_patterns(self.row_clues[i], self.num_cols)
			self.current_row_pattern_indices[i] = list(range(len(self.row_patterns[i])))

		for j in range(self.num_cols):
			self.col_patterns[j] = self.generate_line_patterns(self.col_clues[j], self.num_rows)
			self.current_col_pattern_indices[j] = list(range(len(self.col_patterns[j])))

	def solve(self) -> list[list[list[CellState]]]:
		self.solutions.clear()

		if not self.propagate_constraints():
			return self.solutions

		self.backtrack(0)
		return self.solutions

	def generate_patterns_recursive(
		self,
		clues: list[int],
		line_length: int,
		current_clue_idx: int,
		current_pattern: list[CellState],
		result_patterns: list[list[CellState]],
		start_pos: int = 0,
	) -> None:
		if current_clue_idx == len(clues):
			filled_pattern = current_pattern.copy()
			for i, state in enumerate(filled_pattern):
				if state == UNKNOWN:
					filled_pattern[i] = EMPTY
			if self.is_pattern_valid(filled_pattern, clues):
				result_patterns.append(filled_pattern)
			return

		block_length = clues[current_clue_idx]
		max_start = line_length - block_length
		if max_start < start_pos:
			return

		for pos in range(start_pos, max_start + 1):
			can_place = True

			for offset in range(block_length):
				if current_pattern[pos + offset] == EMPTY:
					can_place = False
					break

			if can_place and pos + block_length < line_length:
				next_cell = current_pattern[pos + block_length]
				if next_cell == FILLED:
					can_place = False

			if not can_place:
				continue

			original_pattern = current_pattern.copy()

			for offset in range(block_length):
				current_pattern[pos + offset] = FILLED

			if pos + block_length < line_length:
				current_pattern[pos + block_length] = EMPTY

			next_start = pos + block_length + 1
			self.generate_patterns_recursive(
				clues,
				line_length,
				current_clue_idx + 1,
				current_pattern,
				result_patterns,
				next_start,
			)

			current_pattern[:] = original_pattern

	def generate_line_patterns(self, clues: list[int], line_length: int) -> list[list[CellState]]:
		result_patterns: list[list[CellState]] = []
		current_pattern = [UNKNOWN for _ in range(line_length)]

		if not clues:
			result_patterns.append([EMPTY for _ in range(line_length)])
			return result_patterns

		self.generate_patterns_recursive(clues, line_length, 0, current_pattern, result_patterns)
		return result_patterns

	def is_pattern_valid(self, pattern: list[CellState], clues: list[int]) -> bool:
		current_clues: list[int] = []
		current_filled_count = 0

		for cell in pattern:
			if cell == FILLED:
				current_filled_count += 1
			else:
				if current_filled_count > 0:
					current_clues.append(current_filled_count)
					current_filled_count = 0

		if current_filled_count > 0:
			current_clues.append(current_filled_count)

		return current_clues == clues

	def backtrack(self, row_idx: int) -> bool:
		if row_idx == self.num_rows:
			self.solutions.append([row.copy() for row in self.grid])
			return True

		original_grid = [row.copy() for row in self.grid]
		original_row_pattern_indices = [indices.copy() for indices in self.current_row_pattern_indices]
		original_col_pattern_indices = [indices.copy() for indices in self.current_col_pattern_indices]

		found_any = False

		for pattern_idx in self.current_row_pattern_indices[row_idx]:
			pattern = self.row_patterns[row_idx][pattern_idx]
			possible = True
			temp_grid = [row.copy() for row in original_grid]

			for c in range(self.num_cols):
				if temp_grid[row_idx][c] != UNKNOWN and temp_grid[row_idx][c] != pattern[c]:
					possible = False
					break
				temp_grid[row_idx][c] = pattern[c]

			if not possible:
				continue

			self.grid = temp_grid

			if self.propagate_constraints():
				if self.backtrack(row_idx + 1):
					found_any = True

			self.grid = [row.copy() for row in original_grid]
			self.current_row_pattern_indices = [indices.copy() for indices in original_row_pattern_indices]
			self.current_col_pattern_indices = [indices.copy() for indices in original_col_pattern_indices]

		return found_any

	def propagate_constraints(self) -> bool:
		changed = True
		while changed:
			changed = False

			for r in range(self.num_rows):
				new_row_indices: list[int] = []

				for p_idx in self.current_row_pattern_indices[r]:
					pattern = self.row_patterns[r][p_idx]
					is_compatible = True
					for c in range(self.num_cols):
						if self.grid[r][c] != UNKNOWN and self.grid[r][c] != pattern[c]:
							is_compatible = False
							break
					if is_compatible:
						new_row_indices.append(p_idx)

				if not new_row_indices:
					return False

				if len(new_row_indices) < len(self.current_row_pattern_indices[r]):
					self.current_row_pattern_indices[r] = new_row_indices
					changed = True

				if self.current_row_pattern_indices[r]:
					for c in range(self.num_cols):
						first_state = self.row_patterns[r][self.current_row_pattern_indices[r][0]][c]
						all_same = True

						for i in range(1, len(self.current_row_pattern_indices[r])):
							if self.row_patterns[r][self.current_row_pattern_indices[r][i]][c] != first_state:
								all_same = False
								break

						if all_same and self.grid[r][c] == UNKNOWN:
							if self.update_grid_cell(r, c, first_state):
								changed = True
							else:
								return False

			for c in range(self.num_cols):
				new_col_indices: list[int] = []

				for p_idx in self.current_col_pattern_indices[c]:
					pattern = self.col_patterns[c][p_idx]
					is_compatible = True
					for r in range(self.num_rows):
						if self.grid[r][c] != UNKNOWN and self.grid[r][c] != pattern[r]:
							is_compatible = False
							break
					if is_compatible:
						new_col_indices.append(p_idx)

				if not new_col_indices:
					return False

				if len(new_col_indices) < len(self.current_col_pattern_indices[c]):
					self.current_col_pattern_indices[c] = new_col_indices
					changed = True

				if self.current_col_pattern_indices[c]:
					for r in range(self.num_rows):
						first_state = self.col_patterns[c][self.current_col_pattern_indices[c][0]][r]
						all_same = True

						for i in range(1, len(self.current_col_pattern_indices[c])):
							if self.col_patterns[c][self.current_col_pattern_indices[c][i]][r] != first_state:
								all_same = False
								break

						if all_same and self.grid[r][c] == UNKNOWN:
							if self.update_grid_cell(r, c, first_state):
								changed = True
							else:
								return False

		return True

	def update_grid_cell(self, r: int, c: int, state: CellState) -> bool:
		if self.grid[r][c] != UNKNOWN and self.grid[r][c] != state:
			return False
		self.grid[r][c] = state
		return True

	def is_solution_valid(self) -> bool:
		for r in range(self.num_rows):
			row_cells = [self.grid[r][c] for c in range(self.num_cols)]
			if not self.is_pattern_valid(row_cells, self.row_clues[r]):
				return False

		for c in range(self.num_cols):
			col_cells = [self.grid[r][c] for r in range(self.num_rows)]
			if not self.is_pattern_valid(col_cells, self.col_clues[c]):
				return False

		return True


def _format_grid(grid: Iterable[Iterable[CellState]]) -> str:
	symbols = {
		UNKNOWN: "?",
		EMPTY: ".",
		FILLED: "#",
	}
	return "\n".join(" ".join(symbols[cell] for cell in row) for row in grid)


if __name__ == "__main__":
	row_clues = [[5], [4], [3, 3], [7, 2], [8, 2], [2, 3, 5], [10], [9, 5], [11, 3], [3, 3, 3, 3], [2, 5, 3, 2], [2, 2, 5, 1], [1, 2, 2, 3], [2, 3, 3], [3, 2, 2], [2, 2, 2], [2, 1], [3], [3], [3]]
	col_clues = [[1], [3], [2, 3], [3, 5], [3, 3, 3], [1, 3, 2, 6], [1, 2, 2, 8], [2, 3, 2, 5], [2, 8], [3, 6, 1], [4, 5, 3], [7, 5], [5, 3], [2, 4], [3, 5, 2], [3, 6], [3, 3], [4], [5], [2]]
	solver = NonogramSolver(row_clues, col_clues)
	solutions = solver.solve()

	print(f"solutions: {len(solutions)}")
	for index, solution in enumerate(solutions, start=1):
		print(f"solution {index}")
		print(_format_grid(solution))
