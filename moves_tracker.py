from enum import Enum


class Operator(Enum):
    RED = 1
    WHITE = 2
    INITIAL = 3


class Item:
    """
    Item represents a step which done or in the process of being done.
    """
    def __init__(self, cell, flipped_list, operator: Operator, valid_moves_list):
        self.cell = cell
        self.flipped_list = flipped_list
        self.valid_moves_list = valid_moves_list
        self.operator = operator


class MovesTracker:
    """
    Manages tracking of moves in the game.
    - Attributes:
        - main_stack: Stack to store main moves.
        - redo_stack: Stack to store moves that have been undone.
        - total_steps: Total number of steps taken in the game.
        - displayed_step: Step currently displayed.
    """
    def __init__(self):
        self.main_stack = list()
        self.redo_stack = list()
        self.total_steps = 0
        self.displayed_step = 0

    def add_item(self, cell, flipped_list, operator: Operator, valid_moves_list):
        self.main_stack.append(Item(cell, flipped_list, operator, valid_moves_list))

    def set_move(self, cell, flipped_list):
        """
        Set the selected cell on the last move and the cells which flipped as a result.
        """
        self.main_stack[-1].cell = cell
        self.main_stack[-1].flipped_list = flipped_list

        if self.main_stack[-1].operator is not Operator.INITIAL:
            self.displayed_step += 1
            self.total_steps += 1

    def get_current_valid_moves(self):
        """
        Returns list of the valid moves of the current step.
        """
        return self.main_stack[-1].valid_moves_list

    def undo(self):
        """
        Reverts the most recent move in the step tracking system.
        :return:
            -Lists of valid moves before and after the undo.
            - List of cells flipped by the second-to-last move.
            - Flag indicating if it's the last move.
            - Description of the move in order to update the title content.
        """
        is_last = False

        first_item = self.main_stack.pop()
        self.redo_stack.append(first_item)
        second_item = self.main_stack[-1]

        self.displayed_step -= 1
        if self.displayed_step == 0:
            is_last = True

        if self.total_steps-self.displayed_step != 1:
            sub_desc = self.describe_move(self.redo_stack[-1])
        else:
            sub_desc = self.describe_move(self.main_stack[-2])

        return first_item.valid_moves_list, second_item.valid_moves_list, second_item.flipped_list, is_last, sub_desc,\
            second_item.operator

    def redo(self):
        """
        Reapplies the last undone move within the step tracking system.
        :return:
            - Lists of valid moves before and after the redo.
            - Cell of the first move to redo.
            - Required color for the move.
            - List of cells flipped by the redo.
            - Flag indicating if it's the last move.
            - Description of the move in order to update the title content.
        """
        is_last = False
        self.displayed_step += 1

        first_item = self.main_stack[-1]

        second_item = self.redo_stack.pop()
        self.main_stack.append(second_item)
        req_color = first_item.operator

        if not self.redo_stack:
            is_last = True

        sub_desc = self.describe_move(first_item)
        return first_item.valid_moves_list, first_item.cell, req_color, first_item.flipped_list, \
            second_item.valid_moves_list, is_last, sub_desc

    def describe_move(self, item: Item):
        """
        Takes an item and generates a string describing the move, used for updating subtitle content.
        """
        if item.cell is None:
            return "Actual State 0\t|\tDisplayed state 0\n"

        if self.displayed_step == 0:
            move_id = '-'
            item.operator = Operator.INITIAL
        else:
            move_id = item.cell[0] * 8 + item.cell[1]
        return "Actual State {}\t|\tDisplayed state {}\nAction {}-{}".format(self.total_steps,
                                                                             self.displayed_step,
                                                                             item.operator,
                                                                             move_id)

    def describe_last_move(self):
        return self.describe_move(self.main_stack[-1])

    def is_board_active(self):
        """
        Checks if the actual current step is the displayed step.
        """
        if self.total_steps == self.displayed_step:
            return True
        return False
