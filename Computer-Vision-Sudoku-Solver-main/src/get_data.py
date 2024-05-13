import os
import pandas as pd
from src.generate import generate_puzzle

def get_data(n):
    # Check if the CSV file already exists
    csv_file = 'data/puzzles.csv'
    if os.path.exists(csv_file):
        # Read existing puzzles from the CSV file
        df = pd.read_csv(csv_file)
    else:
        # If the file doesn't exist, start with an empty DataFrame
        df = pd.DataFrame(columns=['quizzes', 'solutions'])

    # Generate and append new puzzles to the DataFrame
    for _ in range(n):
        solution, puzzle = generate_puzzle(False)
        df = df._append({'quizzes': puzzle, 'solutions': solution}, ignore_index=True)

    # Save puzzles to CSV file
    df.to_csv(csv_file, index=False)
