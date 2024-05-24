import tkinter as tk
from tkinter import messagebox
import subprocess
import math
import os

generated_board = []
field_size = 0 # this will store root of the actual size

def create_empty_board(size):
    board = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(None)
        board.append(row)
    return board

def is_valid_number(number, size):
    try:
        num = int(number)
        return 1 <= num <= size
    except ValueError:
        return False

def validate_entry(entry, size):
    entry_value = entry.get()
    if entry_value and not is_valid_number(entry_value, size):
        entry.config(fg="red")  # Set text color to red for invalid input
    else:
        entry.config(fg="black")  # Set text color back to black for valid input

def generate_board():
    global field_size

    try:
        field_size = int(size_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter a valid integer")
        return

    size = field_size ** 2
    new_board = create_empty_board(size)

    for i in range(size):
        for j in range(size):
            entry = tk.Entry(board_frame, width=4)  # Adjust the width for larger fields
            entry.grid(row=i, column=j, padx=1, pady=1)
            entry.bind("<FocusOut>", lambda event, e=entry: validate_entry(e, field_size**2))
            new_board[i][j] = entry
            
    solve_button.config(state="normal")
    
    global generated_board
    generated_board = new_board

def get_board_from_entries(int_board, tk_board):
    """
    Fetches values from the tkinter Entry widgets and places them in the board.
    If an entry cannot be converted to an integer, it is kept None.
    """
    for i, row in enumerate(tk_board):
        for j, entry_widget in enumerate(row):
            try:
                int_board[i][j] = int(entry_widget.get())
            except ValueError:
                pass

    return int_board

def create_prolog_file(int_board, tk_board):
    """
    Creates a board and size predicates in prolog.
    """
    int_board = get_board_from_entries(int_board, tk_board)

    size = field_size ** 2

    if (math.sqrt(size) % 1) != 0:
        size_entry.config(fg="red")
    else:
        size_entry.config(fg="black")

    with open("sudoku_input.pl", "w") as prolog_file:
        size_predicate =  f"size(X) :- X is {field_size}, !.\n"
        prolog_file.write(size_predicate)

        prolog_file.write("board(X) :- X =\n[\n")
        for i, row in enumerate(int_board):
            prolog_file.write("[")
            for j, value in enumerate(row):
                if value is None:
                    prolog_file.write("_")
                else:
                    prolog_file.write(str(value))

                if j < len(row) - 1:
                    prolog_file.write(",")
            prolog_file.write("]")
            if i < len(int_board) - 1:
                prolog_file.write(",\n")
        prolog_file.write("\n], !.\n")

def solve_sudoku():
    board = create_empty_board(field_size**2)
    create_prolog_file(board, generated_board)


    try:
        # remove the old output file if it exists
        if os.path.exists("sudoku_output.txt"):
            os.remove("sudoku_output.txt")

        # Run the Prolog script
        subprocess.run(["swipl", "-q", "-f", "sudoku.pl"])

        sudoku_output = None

        # Read the output file
        if (os.path.exists("sudoku_output.txt")):
            with open("sudoku_output.txt", "r") as output_file:
                sudoku_output = output_file.read()

        if sudoku_output:
            solution = [[int(v) for v in line.replace("[","").replace("]","").split(",")] for line in sudoku_output.strip().split('\n')]
            # Use the parsed solution to fill generated_board.
            # Set "fg" to green for entries that were originally empty.
            for row_sol, row_gen in zip(solution, generated_board):
                for val, entry_widget in zip(row_sol, row_gen):
                    if not entry_widget.get():
                        entry_widget.config(fg="green")
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, val)

    except Exception as e:
        print(f"An error occurred in Prolog: {str(e)}")

# Create the main window
root = tk.Tk()
root.title("Sudoku Solver")

# Create a frame for the Sudoku board
board_frame = tk.Frame(root)
board_frame.pack(padx=10, pady=10)

# Create a label and entry for board size
size_label = tk.Label(root, text="Enter Field Size (e.g., 3 for 9x9 board):")
size_label.pack()
size_entry = tk.Entry(root)
size_entry.pack()

# Create a button to generate the board
generate_button = tk.Button(root, text="Generate Board", command=generate_board)
generate_button.pack()

# Create a button to solve the Sudoku
solve_button = tk.Button(root, text="Solve Sudoku", state="disabled", command=solve_sudoku)
solve_button.pack()

root.mainloop()