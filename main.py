"""
This module implements the Reversi game with GUI using Tkinter. It includes functions for making moves,
managing the game state, handling undo/redo operations, capturing screenshots of game states,
and executing methodical moves based on specified heuristics.

Note: Put attention to update the `_FOLDER_PATH` variable, to specify the folder where the screenshots should be saved.
"""
import os
import random
import tkinter as tk
from tkinter import messagebox
from moves_tracker import Operator, MovesTracker
import pyautogui
import heuristics
import json

_RED_COLOR = "#E78775"
_WHITE_COLOR = "#F6F5F2"
_BASIC_COLOR = "#B0A695"
_BUTTONS_COLOR = "#F3EEEA"
_MARK_COLOR = "#E6FF94"

_BOARD_SIZE = 8
DEFAULT_FOLDER_PATH = "./ReversiGame"


class Reversi:
    DIRECTIONS = [
        (0, -1),  # Up
        (1, -1),  # Up-Right
        (1, 0),  # Right
        (1, 1),  # Down-Right
        (0, 1),  # Down
        (-1, 1),  # Down-Left
        (-1, 0),  # Left
        (-1, -1),  # Up-Left
    ]

    def __init__(self, master):
        # Initializing counters and a moves tracker
        self.moves_tracker = MovesTracker()
        self.white_counter = 2
        self.red_counter = 2
        self.result_content, self.described_action, self.subtitle, self.result_subtitle, self.title = "", "", None, None, None
        self.board_frame, self.save_btn, self.prev_step_btn, self.next_step_btn = None, None, None, None
        self.folder_path = self.load_folder_path()  # Load the required path from the configuration file.

        # Initializing the gui and creating the board
        self.initialize_gui(master)
        self.board = [[None for _ in range(_BOARD_SIZE)] for _ in range(_BOARD_SIZE)]
        self.create_board()
        self.initialize_board()

        # Start the game
        self.current_player = Operator.RED
        self.moves_tracker.add_item(None, None, self.current_player, self.get_valid_moves())
        self.mark(self.moves_tracker.get_current_valid_moves(), _MARK_COLOR)

    # Load folder path from configuration file or use default
    def load_folder_path(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                folder_path = config.get("folder_path", DEFAULT_FOLDER_PATH)
        except FileNotFoundError:
            folder_path = DEFAULT_FOLDER_PATH
        return folder_path

    def initialize_gui(self, master):
        # Defining basic details
        self.master = master
        self.master.title("Reversi Game")
        self.master.geometry("600x700")

        # Frame for the title and subtitle that describes the situation
        title_frame = tk.Frame(self.master)
        title_frame.pack(side="top", fill="x")

        self.title = tk.Label(title_frame, text="Reversi Game", font=("Helvetica", 16, "bold"))
        self.title.pack(pady=(15, 0))

        self.described_action = "Actual State {}\t|\tDisplayed state {}\n".format(self.moves_tracker.total_steps,
                                                                                self.moves_tracker.displayed_step)
        self.subtitle = tk.Label(title_frame, text=self.described_action, font=("Helvetica", 12))
        self.subtitle.pack(pady=(0, 15))

        # Frame for the main game board
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(side="top", pady=(20, 0))

        # Frame for the result label
        result_subtitle_frame = tk.Frame(self.master)
        result_subtitle_frame.pack(side="top", fill="x", pady=(20, 0))

        self.result_content = "Red: {} disks\t|\t White: {} disk|\t Total: {} disks".format(self.red_counter,
                                                                                            self.white_counter,
                                                                                            self.white_counter + self.red_counter)
        self.result_subtitle = tk.Label(result_subtitle_frame, text=self.result_content, font=("Lato", 13))
        self.result_subtitle.pack(pady=(5, 5))

        # Frame for the undo and redo buttons
        navigation_frame = tk.Frame(self.master)
        navigation_frame.pack(side="bottom", pady=(5, 20))

        self.save_btn = tk.Button(navigation_frame, text="Save Steps", bg=_BUTTONS_COLOR, command=self.save_all_steps)
        self.save_btn.pack(side="left", padx=(20, 10))

        self.prev_step_btn = tk.Button(navigation_frame, text="Previous Step", bg=_BUTTONS_COLOR,
                                       command=self.undo_step)
        self.prev_step_btn.config(state="disabled")
        self.prev_step_btn.pack(side="left", padx=(20, 10))

        self.next_step_btn = tk.Button(navigation_frame, text="Next Step", bg=_BUTTONS_COLOR, command=self.redo_step)
        self.next_step_btn.config(state="disabled")
        self.next_step_btn.pack(side="left")

    def create_board(self):
        for row in range(_BOARD_SIZE):
            for col in range(_BOARD_SIZE):
                button = tk.Button(self.board_frame, bg=_BASIC_COLOR, width=4, height=2,
                                   command=lambda r=row, c=col: self.make_move(r, c))
                button.grid(row=row, column=col)
                self.board[row][col] = button

    # Creating dynamically board according to the required board size
    def initialize_board(self):
        center = _BOARD_SIZE // 2

        initial_positions = [
            (center - 1, center - 1, _RED_COLOR),
            (center - 1, center, _WHITE_COLOR),
            (center, center - 1, _WHITE_COLOR),
            (center, center, _RED_COLOR),
        ]

        for row, col, color in initial_positions:
            self.board[row][col].config(bg=color)
            self.moves_tracker.add_item((row, col), None, Operator.INITIAL, None)

    def mark(self, cells_list, color):
        """
        Apply the specified color to the given list of cells on the board.
        """
        if not cells_list:
            return

        for cell in cells_list:
            self.board[cell[0]][cell[1]]['bg'] = color

    def flip(self, cells_list):
        """
        Flip the colors of the specified cells on the board (Red <--> White)
        Parameters:
        cells_list (list of tuples): A list of (row, col) tuples representing the cells to be reversed.
        """
        if not cells_list:
            return

        flip_into_color = _RED_COLOR if self.board[cells_list[0][0]][cells_list[0][1]]['bg'] == _WHITE_COLOR else _WHITE_COLOR

        for cell in cells_list:
            self.board[cell[0]][cell[1]]['bg'] = flip_into_color

        if flip_into_color == _RED_COLOR:
            self.red_counter += len(cells_list)
            self.white_counter -= len(cells_list)
        else:
            self.white_counter += len(cells_list)
            self.red_counter -= len(cells_list)

        self.set_result_content()

    def set_result_content(self):
        """
        Update the game result content based on the current state of the board.
        """
        self.result_content = "Red: {} disks\t|\t White: {} disk|\t Total: {} disks".format(self.red_counter,
                                                                                            self.white_counter,
                                                                                            self.white_counter + self.red_counter)
        self.result_subtitle.config(text=self.result_content)

    def undo_step(self):
        """
        Revert the board to its state before the last move using the moves-tracker.

        This method updates the board, manages the enable/disable state of the undo/redo buttons,
        and updates the subtitles accordingly.
        """
        self.next_step_btn.config(state="normal")  # Enable next step button
        current_valid_moves, prev_valid_moves, flipped_list, is_last, sub_desc, operator = self.moves_tracker.undo()
        self.mark(current_valid_moves, _BASIC_COLOR)  # Cancel the marks of the current valid moves
        self.mark(prev_valid_moves, _MARK_COLOR)  # Mark the previous valid moves

        # Manage the Counters
        if operator == Operator.RED:
            self.red_counter -= 1
        else:
            self.white_counter -= 1

        if is_last:
            self.prev_step_btn.config(state="disabled")

        self.flip(flipped_list)  # Flip back the list

        self.subtitle.config(text=sub_desc)

    def redo_step(self):
        """
        Reapply the next move that was previously undone and update the UI (it using the moves-tracker).

        This method updates the board, manages the enable/disable state of the undo/redo buttons,
        and updates the subtitles accordingly.
        """
        self.prev_step_btn.config(state="normal")
        cur_valid_moves, cell, req_color, flipped_list, newer_valid_moves, is_last, sub_desc = self.moves_tracker.redo()
        self.mark(cur_valid_moves, _BASIC_COLOR)
        self.board[cell[0]][cell[1]]['bg'] = _RED_COLOR if req_color == Operator.RED else _WHITE_COLOR
        if req_color == Operator.RED:
            self.red_counter += 1
        else:
            self.white_counter += 1

        self.mark(newer_valid_moves, _MARK_COLOR)
        self.flip(flipped_list)
        self.subtitle.config(text=sub_desc)

        if is_last:
            self.next_step_btn.config(state="disabled")

    def make_move(self, row, col):
        """
        Execute a move at the specified cell on the board, and update the game state accordingly.

        This method:
        1. Ensures the board is active for a new move.
        2. Validates the move, showing warnings if invalid.
        3. If valid, updates counters, flips discs, records the move, and updates the UI.
        4. Prints heuristic scores for mobility and positional evaluations.
        5. Switches the current player and marks valid moves for the next turn.
        """
        if not self.moves_tracker.is_board_active():
            messagebox.showwarning("Invalid move", "Before performing a new action, go back to the last state. ")
            return

        status, direction = self.is_valid_move(row, col)
        if status == 0:
            if self.current_player == Operator.RED:
                self.red_counter += 1
            else:
                self.white_counter += 1
            discs_to_flip = self.get_list_to_flip(row, col, direction)
            self.flip(discs_to_flip)
            self.moves_tracker.set_move((row, col), discs_to_flip)

            desc = self.moves_tracker.describe_last_move()
            self.subtitle.config(text=desc)
            self.prev_step_btn.config(state="normal")
            self.mark(self.moves_tracker.get_current_valid_moves(), _BASIC_COLOR)
            self.board[row][col]['bg'] = _RED_COLOR if self.current_player == Operator.RED else _WHITE_COLOR

            # Calculate and print the mobility heuristic score
            board_x = self.convert_board_to_array()
            mobility_score = heuristics.mobility_heuristic(board_x, 1 if self.current_player == Operator.RED else 2)
            print(f"Mobility heuristic score after move by {'RED' if self.current_player == Operator.RED else 'WHITE'}: {mobility_score}")

            # Calculate and print the positional heuristic score
            positional_score = heuristics.positional_heuristic(self.convert_board_to_array(), 1 if self.current_player == Operator.RED else 2)
            print(f"Positional heuristic score after move by {'RED' if self.current_player == Operator.RED else 'WHITE'}: {positional_score}")

            self.current_player = Operator.WHITE if self.current_player == Operator.RED else Operator.RED
            self.moves_tracker.add_item(None, None, self.current_player, self.get_valid_moves())
            self.mark(self.moves_tracker.get_current_valid_moves(), _MARK_COLOR)
        else:
            if status == 1:
                messagebox.showwarning("Invalid Move", "The cell is already occupied")
            elif status == 2:
                messagebox.showwarning("Invalid Move", "OOPS!")

    # Returns status (0-VALID,1-INVALID:occupied,2-INVALID), direction (x,y)
    def is_valid_move(self, row, col):
        # Checking if the cell isn't already occupied
        if self.board[row][col]['bg'] in (_RED_COLOR, _WHITE_COLOR):
            return 1, None

        current_color = _WHITE_COLOR if self.current_player == Operator.WHITE else _RED_COLOR
        opponent_color = _WHITE_COLOR if self.current_player == Operator.RED else _RED_COLOR

        # Iterate through all possible directions
        for dr, dc in self.DIRECTIONS:
            r, c = row + dr, col + dc

            # Check if the first cell in the direction - (r,c) is within bounds
            if not (0 <= r < _BOARD_SIZE and 0 <= c < _BOARD_SIZE):
                continue

            # Check if the first cell in the direction contains an opponent's disc
            if self.board[r][c]['bg'] == opponent_color:
                # Move in the current direction to check for a valid sequence
                while 0 <= r < _BOARD_SIZE and 0 <= c < _BOARD_SIZE:
                    r += dr
                    c += dc

                    # If out of bounds, break the loop (and will move on to check the next direction)
                    if not (0 <= r < _BOARD_SIZE and 0 <= c < _BOARD_SIZE):
                        break

                    # If an empty cell is encountered, break the loop (and will move on to check the next direction)
                    if self.board[r][c]['bg'] == _BASIC_COLOR:
                        break

                    # If a disc of the current player is encountered, the move is valid
                    if self.board[r][c]['bg'] == current_color:
                        return 0, (dr, dc)
        return 2, None

    def get_list_to_flip(self, row, col, direction):
        flipped_list = list()
        opponenet_color = _WHITE_COLOR if self.current_player == Operator.RED else _RED_COLOR

        # Move on in this direction and flip every disc you see
        r, c = row + direction[0], col + direction[1]

        while 0 <= r < _BOARD_SIZE and 0 <= c < _BOARD_SIZE:
            if self.board[r][c]['bg'] == opponenet_color:
                flipped_list.append((r, c))

                r += direction[0]
                c += direction[1]
            else:
                break

        return flipped_list

    # Returns a list of cells that indicate the valid moves
    def get_valid_moves(self):
        """
            Get a list of valid moves for the current player.
            Notes:
            - This method iterates through each cell on the game board and checks if it's a valid move.
        """
        valid_moves_list = list()

        for row in range(0, _BOARD_SIZE):
            for col in range(0, _BOARD_SIZE):
                status, _ = self.is_valid_move(row, col)
                if status == 0:
                    valid_moves_list.append((row, col))

        return valid_moves_list

    def capture_screenshot(self, folder_path):
        """
        Captures a screenshot of the current window and saves it to the specified folder path.
        """
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        pyautogui.screenshot(folder_path, region=(x, y, w, h))

    def save_all_steps(self):
        """
        Saves screenshots of all the steps of an operation in a designated folder.
        """
        os.makedirs(self.folder_path, exist_ok=True)

        current_step = self.moves_tracker.displayed_step

        step = current_step
        while step > 1:
            self.undo_step()
            step -= 1
            self.master.update_idletasks()  # Wait for GUI to update

        # Take a screenshot of the initial state
        self.capture_screenshot(f"{self.folder_path}/step_0.png")

        # Take screenshots while reverting back to the current step
        step = 1
        while step <= current_step - 1:
            self.redo_step()
            self.master.update_idletasks()  # Wait for GUI to update
            self.capture_screenshot(f"{self.folder_path}/step_{step}.png")
            step += 1

    def start_methodical_moves(self, num_of_captures, num_of_discs=None, player1_mode=None, player2_mode=None, steps_ahead=1):
        """
        Start the process of making moves methodically according to the specified requirements.

        Args:
            num_of_captures (int): The number of screenshots to capture during the process.
            num_of_discs (int, optional): The maximum number of discs to be placed on the board. Defaults to None (until the end)
            player1_mode (str, optional): The mode of player 1 ('random', 'H1', 'H2', or None). Defaults to None (chooses the first valid move)
            player2_mode (str, optional): The mode of player 2 ('random', 'H1', 'H2', or None). Defaults to None (chooses the first valid move)
            steps_ahead (int, optional): The number of steps ahead to consider in the decision-making process. Defaults to 1.
        """
        captured_counter = 0

        self.master.update_idletasks()
        self.capture_screenshot(f"{self.folder_path}/step_0.png")
        self.master.update_idletasks()
        captured_counter += 1

        if num_of_discs is not None:
            max_discs = min(_BOARD_SIZE * _BOARD_SIZE, num_of_discs)
        else:
            max_discs = _BOARD_SIZE * _BOARD_SIZE

        while True:
            if self.red_counter + self.white_counter == max_discs:
                return
            else:
                valid_moves = self.moves_tracker.get_current_valid_moves()
                current_mode = player1_mode if self.current_player == Operator.RED else player2_mode

                if valid_moves:
                    if current_mode == 'random':
                        if self.moves_tracker.total_steps == 0:
                            chosen_move = valid_moves[0]  # In the initial state, the 4 possible actions are symmetric.
                            print(valid_moves)
                        else:
                            chosen_move = random.choice(valid_moves)
                    elif current_mode == 'H1':
                        if steps_ahead > 1:
                            chosen_move = heuristics.minimax_decision(self.convert_board_to_array(), valid_moves, steps_ahead, 1 if self.current_player == Operator.RED else 2)
                        else:
                            chosen_move = heuristics.choose_move_with_best_mobility(self.convert_board_to_array(), valid_moves, 1 if self.current_player == Operator.RED else 2)
                    elif current_mode == 'H2':
                        chosen_move = heuristics.choose_move_with_best_positional_heuristic(self.convert_board_to_array(), valid_moves, 1 if self.current_player == Operator.RED else 2)
                    else:
                        chosen_move = valid_moves[0]

                    self.make_move(chosen_move[0], chosen_move[1])
                    self.master.update_idletasks()

                    # Capture the screenshot of the current step
                    if captured_counter <= num_of_captures:
                        self.capture_screenshot(f"{self.folder_path}/step_{captured_counter}.png")
                        self.master.update_idletasks()
                        captured_counter += 1
                else:  # The run has arrived to inaccessible state.
                    if captured_counter < num_of_captures:
                        messagebox.showwarning("Inaccessible state",
                                               "The depth of the tree in the selected branch is less than n.")
                    return

    def convert_board_to_array(self):
        """
        :return: Convert the current state of the game board into a 2D array representation.
        - Each cell in the array represents the color of the corresponding position on the game board:
          - 0: Empty or marked as a valid move
          - 1: Red disc
          - 2: White disc
        """
        board_array = []
        for row in range(_BOARD_SIZE):
            board_row = []
            for col in range(_BOARD_SIZE):
                color = self.board[row][col]['bg']
                if color == _BASIC_COLOR or color == _MARK_COLOR:
                    board_row.append(0)
                elif color == _RED_COLOR:
                    board_row.append(1)
                elif color == _WHITE_COLOR:
                    board_row.append(2)
            board_array.append(board_row)
        return board_array
