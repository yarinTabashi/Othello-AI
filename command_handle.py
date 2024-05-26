import argparse


def parse_arguments():
    """
    Parse command-line arguments for the Reversi game.
    Arguments include options to run the program, display actions, play methodically or randomly, apply heuristics,
    or simulate moves ahead.
    """
    parser = argparse.ArgumentParser(description="Reversi game arguments")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-run', action='store_true', help="Run the program")
    group.add_argument('-displayAllActions', type=int, help="Display all actions with a specific number of discs")
    group.add_argument('-methodical', type=int, help="Methodical player with depth")
    group.add_argument('-random', type=int, help="Random player with moves")
    parser.add_argument('-heuristics', nargs='*', choices=['H1', 'H2'], help="Heuristics for players (e.g., H1 H2)")
    group.add_argument('-ahead', type=int, help="Simulation with the best heuristic function, consider 2 steps ahead. ")
    return parser.parse_args()