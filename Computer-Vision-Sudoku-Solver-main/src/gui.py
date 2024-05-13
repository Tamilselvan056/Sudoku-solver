import tkinter as tk
from tkinter import ttk
from src.generate import generate_puzzle
from src.camera import take_picture
from src.extract_puzzle import extract
import time
import cv2 as cv


def validate_input(row, col, value):
	"""
	Validate the input value for a Sudoku cell.

	Args:
		row (int): The row index of the cell.
		col (int): The column index of the cell.
		value (int): The value to be validated.

	Returns:
		bool: True if the input value is correct for the cell, False otherwise.
	"""
	return solution[row][col] == value

def get_percentage_solved():
    """
    Calculate and return the percentage of cells solved.

    Returns:
        float: The percentage of cells solved.
    """
    global initial_empty_cells
    empty_cells = sum(row.count(0) for row in puzzle)
    percentage_solved = (initial_empty_cells - empty_cells) / initial_empty_cells * 100
    return percentage_solved

def get_time_spent():
    """
    Get the time spent solving the puzzle.

    Returns:
        str: The formatted time spent in the format HH:MM:SS.
    """
    if start_time == 0:
        return "00:00:00"
    elapsed_time = int(time.time() - start_time)
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60
    return f"{minutes:02}:{seconds:02}"

def solve_puzzle():
	"""
	Fill the puzzle with the correct solution.

	This function replaces the user's inputs with the correct solution values.
	"""
	global entries
	for i in range(9):
		for j in range(9):
			entry = entries[i][j]
			entry.delete(0, tk.END)
			entry.insert(tk.END, str(solution[i][j]))
			entry.config(foreground="black")

def fill():
	global entries, start_time, initial_empty_cells
	initial_empty_cells = 0
	for i in range(9):
		for j in range(9):
			entry = entries[i][j]
			entry.delete(0, tk.END)
			value = puzzle[i][j]
			if value != 0:
				entry.insert(tk.END, str(value))
			else:
				initial_empty_cells += 1
			entry.config(foreground="black")
	start_time = time.time()

def reset_puzzle():
	"""
	Reset the puzzle to its initial state.

	This function clears the user's inputs and restores the original puzzle state.
	"""
	global entries, puzzle, initial_empty_cells, start_time
	tmp1, tmp2 = start_time, initial_empty_cells
	fill()
	start_time, initial_empty_cells = tmp1, tmp2

def new_puzzle(difficult=True):
	"""
	Generate a new random Sudoku puzzle.

	This function generates a new Sudoku puzzle and updates the GUI with the new puzzle.
	"""
	global solution, puzzle, wrongs
	wrongs = 0
	solution, puzzle = generate_puzzle(difficult)
	fill()

def from_picture():
	global solution, puzzle, entries, start_time
	frame = take_picture()
	cv.imshow("Picca", frame)
	solution, puzzle, _, _ = extract(frame)
	fill()

def on_button_click(row, col, button):
	"""
	Handle the button click event for a Sudoku cell.

	Args:
		row (int): The row index of the cell.
		col (int): The column index of the cell.
		button (tk.StringVar): The StringVar associated with the cell's Entry widget.
	"""
	global wrongs
	value = button.get()
	if value:
		value = int(button.get())
		if validate_input(row, col, value):
			puzzle[row][col] = value
			button.config(foreground="black")
		else:
			button.config(foreground="red")
			wrongs += 1

def main():
	"""
	Main function to initialize the Sudoku Solver GUI.
	"""
	global solution, puzzle, initial_empty_cells, wrongs, start_time
	wrongs = initial_empty_cells = 0
	solution, puzzle = generate_puzzle(difficult=False)
	start_time = time.time()
	root = tk.Tk()
	root.title("Sudoku Solver")

	grid_frame = tk.Frame(root)
	grid_frame.pack()
	entries_info = {} 

	global entries
	entries = []
	for i in range(9):
		row_entries = []
		for j in range(9):
			value = puzzle[i][j]
			back_col = "lightgrey" if ((i//3) + (j//3)) % 2 else "white"
			entry = tk.Entry(grid_frame, width=3, justify="center", font=("Arial", 20), bg=back_col, bd=1, relief="solid")
			if value != 0:
				entry.insert(tk.END, str(value))
			else:
				initial_empty_cells += 1
			entry.grid(row=i, column=j, padx=0, pady=0, ipady=5)
			entries_info[entry] = (i, j)    
			entry.bind('<FocusOut>', lambda event, row=i, col=j, entry=entry: on_button_click(row, col, entry))
			row_entries.append(entry)

		entries.append(row_entries)

	button_frame1 = tk.Frame(root)
	button_frame1.pack(pady=10)

	reset_button = ttk.Button(button_frame1, text="Puzzle", command=reset_puzzle, style="My.TButton")
	reset_button.pack(side="left", padx=5)

	solve_button = ttk.Button(button_frame1, text="Solution", command=solve_puzzle, style="My.TButton")
	solve_button.pack(side="left", padx=5)

	button_frame2 = tk.Frame(root)
	button_frame2.pack(pady=10)

	new_button = ttk.Button(button_frame2, text="Easy", command=lambda: new_puzzle(difficult=False), style="My.TButton")
	new_button.pack(side="left", padx=5)
	
	new_button = ttk.Button(button_frame2, text="Hard", command=new_puzzle, style="My.TButton")
	new_button.pack(side="left", padx=5)

	button_frame3 = tk.Frame(root)
	button_frame3.pack(pady=10)

	# Add the Capture Frames button
	capture_button = ttk.Button(button_frame3, text="From Picture", command=from_picture, style="My.TButton")
	capture_button.pack(side="left", padx=5)

	# Define a custom style for the ttk.Buttons
	style = ttk.Style()
	style.configure("My.TButton", font=("Arial", 16), foreground="black", background="#EAEAEA", borderwidth=0, padding=10)
	
	# Function to update the status bar with the current statistics.
	def update_status_bar():
		percentage_solved = get_percentage_solved()
		status_var.set(f"Percentage Solved: {percentage_solved:.2f}% | Wrong Count: {wrongs} | Time Spent: {get_time_spent()}")
		# Schedule the next update after 1000 milliseconds (1 second).
		root.after(1000, update_status_bar)
	
	# Create a status bar at the bottom of the root window.
	status_var = tk.StringVar()
	status_bar = ttk.Label(root, textvariable=status_var, font=("Arial", 12), relief="sunken", anchor="center")
	status_bar.pack(fill="x", side="bottom")

	update_status_bar()  # Initial status update.

	root.mainloop()


if __name__ == "__main__":
	main()
