# Othello Game With AI
A Python implementation of the classic Othello (Reversi) board game with a graphical user interface, and includes AI algorithms.
such as heuristics and minimax,  that demonstrate the strategic decision-making process.
## Basic Features
- **Graphical User Interface**: Built with Tkinter, providing an interactive experience.
- **Customization**: Customize game settings, including board size and difficulty.
- **Moves Tracker**: Utilizes a stack implementation to store the steps, allowing players to review past moves without altering the current game state.
- **Capture Abillity**: Capture and save screenshots of each step in the game, allowing you to review your moves and strategies. Screenshots are saved locally in a dedicated folder.
- **Mark Valid Moves**: At each step, valid moves are highlighted on the game board, aiding players in strategic decision-making.
## AI Algroithms and Chosen Heuristics
#### Heuristics:
 - ***Mobility Heuristic***- This heuristic evaluates the number of available legal moves for a player. It aims to maximize the player's options while minimizing the opponent's, encouraging flexibility and control over the game.
 - ***Positional Heuristic***:- This heuristic values certain positions on the board more highly, typically corners and edges, as controlling these positions is strategically advantageous in Reversi. It prioritizes moves that lead to gaining or protecting these key areas.

#### To handle decision-making with a search depth greater than 1:

* ***Minimax*** is a recursive algorithm used for choosing the optimal move for a player, assuming that the opponent is also playing optimally. It evaluates the possible future game states, considering both the player's and the opponent's potential moves, to determine the best move to make at any given point in the game.
## Commands
Ensure to set the directory in the ***config.json*** file where captures will be saved.

1. ***Run the game:***
```python
python reversi.py -run
```

2. ***Start the game with a specific number of discs on the board (chooses one of the valid states):***
```python
python reversi.py -displayAllActions n
```

3. ***Execute methodical moves and captures the firist n moves:***
```python
python reversi.py -methodical n
```

4. ***Execute random moves and captures the first for n moves:***
```python
python reversi.py -random n
```

5. ***Start the game using specified heuristics,*** where player 1 uses heuristic HX and player 2 uses heuristic HY. For example:
```python
python reversi.py -heuristics H1 H2
```


## Additional
This project was created as part of the Introduction to AI course (20551) at the Open University.
