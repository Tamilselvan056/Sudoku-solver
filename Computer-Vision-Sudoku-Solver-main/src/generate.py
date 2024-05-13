import random
import copy
from src.test import valid, solve
import time

def generate_configuration():
	"""
	Generate a random valid Sudoku configuration.

	Returns:
		list: A 9x9 list representing the Sudoku configuration.
			Each cell contains a number from 1 to 9.
			Zero (0) represents an empty cell.
	"""
	configuration = [[0]*9 for _ in range(9)]
	rows = [set(range(1,10)) for _ in range(9)]
	columns = [set(range(1,10)) for _ in range(9)]
	squares = [[set(range(1,10)) for r in range(3)] for c in range(3)]

	for r in range(9):
		for c in range(9):
			possibilities = rows[r].intersection(columns[c]).intersection(squares[r//3][c//3])

			if not possibilities:
				return None

			number = random.choice(list(possibilities))

			rows[r].remove(number)
			columns[c].remove(number)
			squares[r//3][c//3].remove(number)

			configuration[r][c] = number

	return configuration

def generate_solution_puzzle():
	"""
	Generate a Sudoku puzzle with a unique solution.

	Returns:
		list: A 9x9 list representing the Sudoku puzzle with a unique solution.
			Each cell contains a number from 1 to 9.
	"""
	while True:
		configuration = generate_configuration()
		if configuration:
			assert valid(configuration) == True
			return configuration

def omit_numbers(solution, difficult):
	"""
	Omit numbers from the given Sudoku solution while ensuring the resulting puzzle has a unique solution.

	Args:
		solution (list): A 9x9 list representing the Sudoku solution.
			Each cell contains a number from 1 to 9.
		attempted_numbers_to_omit (int): The number of cells to omit while generating the puzzle.

	Returns:
		tuple: A tuple containing the following elements:
			list: A 9x9 list representing the Sudoku puzzle.
				Each cell contains a number from 0 to 9, where 0 represents an empty cell.
			int: The number of cells omitted in the puzzle.
	"""
	cells_left = set((r, c) for r in range(9) for c in range(9))
	number_cells_omitted = 0
	configuration = copy.deepcopy(solution)

	def able_to_omit(row, col):
		number = configuration[row][col]
		configuration[row][col] = -1

		def number_possible(r, c):
			for j in range(9):
				if (configuration[r][j] == number or 
					configuration[j][c] == number or 
					configuration[(r//3)*3 + j//3][(c//3)*3 + j%3] == number):
					return False
			configuration[row][col] = number
			return True

		# Check whether an empty cell could contain the number
		for i in range(9):
			if configuration[row][i] == 0:
				if number_possible(row, i):
					return False
			if configuration[i][col] == 0:
				if number_possible(i, col):
					return False
			if configuration[(row//3)*3 + i//3][(col//3)*3 + i%3] == 0:
				if number_possible((row//3)*3 + i//3, (col//3)*3 + i%3):
					return False

		return True

	while cells_left:
		row, column = random.choice(list(cells_left))
		cells_left.remove((row, column))
		# print(number_cells_omitted)
		# print(configuration)

		if not difficult:
			if able_to_omit(row, column):
				configuration[row][column] = 0
				number_cells_omitted += 1
		else:
			tmp = configuration[row][column]
			configuration[row][column] = 0
			a = solve(configuration, True)[1]
			# print(a)
			if a > 1:
				configuration[row][column] = tmp
				# print()
			else:
				number_cells_omitted += 1

	return configuration, number_cells_omitted

def generate_puzzle(difficult=True):
	"""
	Generates a Sudoku puzzle and its unique solution.

    Returns:
		tuple: A tuple containing the following elements:
			list: A 9x9 list representing the Sudoku solution.
				Each cell contains a number from 1 to 9.
			list: A 9x9 list representing the Sudoku puzzle.
				Each cell contains a number from 0 to 9, where 0 represents an empty cell.
    """
	omitted = 0
	# while omitted < 60:
	solution = generate_solution_puzzle()
	puzzle, omitted = omit_numbers(solution, difficult)
	# print(puzzle)
	# print(solution)
	a  = solve(puzzle)[0]
	# print(a)
	assert a == solution  # Uniqueness requirement
	# print(omitted)
	return (solution, puzzle)

if __name__ == "__main__":
	start_time = time.time()
	for _ in range(1):
		generate_puzzle(True)
	print(f"Time elapsed: {time.time() - start_time}")
