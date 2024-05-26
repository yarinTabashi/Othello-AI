_BOARD_SIZE = 8
_POSITIONAL_WEIGHTS = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [10, -2, 5, 1, 1, 5, -2, 10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10, 5, 5, 10, -20, 100]
]


def mobility_heuristic(board, player):
    """
    Evaluate the mobility heuristic for a player on the board.
    """
    opponent = 3 - player  # Assuming players are represented as 1 and 2
    player_moves = len(get_valid_moves(board, player))
    opponent_moves = len(get_valid_moves(board, opponent))
    return player_moves - opponent_moves


def positional_heuristic(board, player):
    """
    It sums up the scores of the player's pieces and subtracts the scores of the opponent's pieces,
    to provide an overall assessment of the board state.
    """
    score = 0
    for i in range(_BOARD_SIZE):
        for j in range(_BOARD_SIZE):
            if board[i][j] == player:
                score += _POSITIONAL_WEIGHTS[i][j]
            elif board[i][j] == 3 - player:  # Assuming 1 for player, 2 for opponent
                score -= _POSITIONAL_WEIGHTS[i][j]
    return score


def choose_move_with_best_mobility(board, valid_moves, player):
    """
    Choose the move with the best mobility for a player.
    """
    best_move = None
    best_mobility_score = -float('inf')
    opponent = 3 - player

    for move in valid_moves:
        row, col = move
        temp_board = copy_board(board)  # Create a copy of the board
        temp_board = simulate_move(temp_board, row, col, player)  # Simulate the move for the current player
        player_mobility = len(get_valid_moves(temp_board, player))
        opponent_mobility = len(get_valid_moves(temp_board, opponent))
        mobility_score = player_mobility - opponent_mobility

        if mobility_score > best_mobility_score:
            best_mobility_score = mobility_score
            best_move = move

    return best_move


def choose_move_with_best_positional_heuristic(board, valid_moves, player):
    """
    Choose the next move based on the positional heuristic.
    """
    best_move = None
    best_score = float('-inf')

    for move in valid_moves:
        row, col = move
        temp_board = copy_board(board)  # Create a copy of the board
        temp_board = simulate_move(temp_board, row, col, player)  # Simulate the move for the current player

        # Calculate the positional heuristic score for the resulting board
        score = positional_heuristic(temp_board, player)

        # Update the best move if the current move has a higher positional heuristic score
        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def minimax_decision(board, valid_moves, depth, current_player):
    """
    Perform a minimax decision to choose the best move.
    """
    best_move = None
    best_score = float('-inf')

    for move in valid_moves:
        # Simulate the move for the current player
        temp_board = copy_board(board)
        temp_board = simulate_move(temp_board, move[0], move[1], current_player)

        # Calculate the opponent's best move using minimax with one less depth
        opponent_moves = get_valid_moves(temp_board, 3 - current_player)
        score, _ = minimax(opponent_moves, depth - 1, False, temp_board, current_player)

        # Evaluate the current move's score
        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def minimax(valid_moves, depth, maximizing_player, board, player):
    """
    Perform the minimax algorithm to determine the best move.
    """
    if depth == 0 or not valid_moves:
        return positional_heuristic(board, player), None  # Evaluate the leaf node

    if maximizing_player:
        max_value = float('-inf')
        best_move = None
        for move in valid_moves:
            # Make the move for the current player
            temp_board = copy_board(board)
            temp_board = simulate_move(temp_board, move[0], move[1], player)

            # Calculate the opponent's best move using minimax with one less depth
            opponent_moves = get_valid_moves(temp_board, 3 - player)
            value, _ = minimax(opponent_moves, depth - 1, False, temp_board, 3 - player)

            if value > max_value:
                max_value = value
                best_move = move

        return max_value, best_move
    else:
        min_value = float('inf')
        best_move = None
        for move in valid_moves:
            # Make the move for the opponent
            temp_board = copy_board(board)
            temp_board = simulate_move(temp_board, move[0], move[1], 3 - player)

            # Calculate the current player's best move using minimax with one less depth
            player_moves = get_valid_moves(temp_board, player)
            value, _ = minimax(player_moves, depth - 1, True, temp_board, player)

            if value < min_value:
                min_value = value
                best_move = move

        return min_value, best_move


# --- Helpers ----
def copy_board(board):
    """
    Create a deep copy of the board.
    """
    return [row[:] for row in board]


def is_within_bounds(row, col):
    """
    Check if a position is within the bounds of the board.
    """
    return 0 <= row < _BOARD_SIZE and 0 <= col < _BOARD_SIZE


def is_valid_move(board, player, row, col, directions):
    """
    Check if a move is valid for a player at a certain position.
    """
    opponent = 3 - player  # Assuming players are represented as 1 and 2

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if is_within_bounds(r, c) and board[r][c] == opponent:
            while is_within_bounds(r, c) and board[r][c] == opponent:
                r += dr
                c += dc
            if is_within_bounds(r, c) and board[r][c] == player:
                return True

    return False


def get_valid_moves(board, player):
    """
    Returns the valid moves for the current player.
    """
    opponent = 3 - player  # Assuming players are represented as 1 and 2
    valid_moves = []

    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]

    for row in range(_BOARD_SIZE):
        for col in range(_BOARD_SIZE):
            if board[row][col] == 0:  # Check only empty cells
                if is_valid_move(board, player, row, col, directions):
                    valid_moves.append((row, col))

    return valid_moves


def simulate_move(board, row, col, player):
    """
    Simulate the effect of a move on the board.
    """
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]
    board[row][col] = player
    for dr, dc in directions:
        r, c = row + dr, col + dc
        if is_within_bounds(r, c) and board[r][c] == 3 - player:
            tiles_to_flip = []
            while is_within_bounds(r, c) and board[r][c] == 3 - player:
                tiles_to_flip.append((r, c))
                r += dr
                c += dc
            if is_within_bounds(r, c) and board[r][c] == player:
                for rr, cc in tiles_to_flip:
                    board[rr][cc] = player

    return board