import command_handle
from main import Reversi
import tkinter as tk


def run_reversi():
    root = tk.Tk()
    game = Reversi(root)
    root.mainloop()


def start_methodical_by_requirements(num_of_captures, num_of_discs=None, player1_mode=None, player2_mode=None, ahead=1):
    """
    Start the Reversi game methodically based on specified requirements (using the start_methodical_moves method).
    :param num_of_captures: The number of screenshots to capture during the process.
    :param num_of_discs: The maximum number of discs to be placed on the board. Defaults to None.
    :param player1_mode: The maximum number of discs to be placed on the board. Defaults to None.
    :param player2_mode: (str, optional): The mode of player 2 ('random', 'H1', 'H2', or None). Defaults to None.
    :param ahead: (int, optional): The number of steps ahead to consider in the decision-making process. Defaults to 1.
    """
    def random_after_gui():
        game = Reversi(root)
        game.start_methodical_moves(num_of_captures, num_of_discs, player1_mode, player2_mode, ahead)

    root = tk.Tk()
    root.after(100, random_after_gui)  # Call methodical_after_gui after a delay
    root.mainloop()


if __name__ == "__main__":
    args = command_handle.parse_arguments()

    if args.run:
        print("Running the program...")
        run_reversi()

    elif args.displayAllActions is not None:
        print(f"Displaying all actions with {args.displayAllActions} discs")
        n = args.displayAllActions
        start_methodical_by_requirements(num_of_captures=n, num_of_discs=n)

    elif args.methodical is not None:
        print(f"Methodical player with depth {args.methodical}")
        start_methodical_by_requirements(num_of_captures=args.methodical)

    elif args.random is not None:
        print(f"Random player with moves {args.random}")
        n = args.random
        start_methodical_by_requirements(num_of_captures=n, player1_mode='random', player2_mode='random')

    elif args.ahead is not None:
        print("Simulation with the best heuristic function, consider 2 steps ahead.")
        start_methodical_by_requirements(num_of_captures=0, player1_mode='H1', player2_mode='H1', ahead=2)

    else:
        heuristics = args.heuristics
        if len(heuristics) == 0:
            print("No heuristic provided. Exiting.")

        elif len(heuristics) == 1:
            print(f"Single heuristic provided. Both players will use {heuristics[0]}")
            if heuristics[0] == 'H1':
                start_methodical_by_requirements(num_of_captures=0, player1_mode='H1', player2_mode='H1')
            else:
                start_methodical_by_requirements(num_of_captures=0, player1_mode='H2', player2_mode='H2')

        elif len(heuristics) == 2:
            print(f"Player 1 will use heuristic {heuristics[0]}, and player 2 will use {heuristics[1]}")
            start_methodical_by_requirements(num_of_captures=0, player1_mode=heuristics[0], player2_mode=heuristics[1])

        else:
            print("Too many heuristics provided. Exiting.")
            exit(1)