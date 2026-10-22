
"""Sudoku board service.

Owns puzzle cells, immutable clues, undo history, and board revision.
Implements specs/board_contract.md.
"""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BoardResult:
    accepted: bool
    reason: str
    revision: int


class Board:
    SIZE = 9
    DIGITS = set(range(1, 10))

    def __init__(self, givens: Sequence[Sequence[int]]):
        if len(givens) != self.SIZE:
            raise ValueError("Board must contain exactly 9 rows")

        for row in givens:
            if len(row) != self.SIZE:
                raise ValueError("Each row must contain exactly 9 cells")

            if any(type(value) is not int or not 0 <= value <= 9
                   for value in row):
                raise ValueError("Cells must be integers from 0 to 9")

        self._grid = [list(row) for row in givens]
        self._givens = {
            (row, col)
            for row in range(9)
            for col in range(9)
            if self._grid[row][col] != 0
        }

        self._history = []
        self.revision = 0

        if not self._valid_grid():
            raise ValueError("Conflicting given clues")

    @staticmethod
    def _valid_index(index):
        return type(index) is int and 0 <= index < 9

    def _check_index(self, index):
        if not self._valid_index(index):
            raise ValueError("Invalid coordinate")

    @staticmethod
    def _no_duplicates(values):
        nonzero = [value for value in values if value != 0]
        return len(nonzero) == len(set(nonzero))

    def _valid_grid(self):
        for index in range(9):
            if not self._no_duplicates(self.inspect_row(index)):
                return False
            if not self._no_duplicates(self.inspect_column(index)):
                return False
            if not self._no_duplicates(self.inspect_box(index)):
                return False
        return True

    def inspect_board(self):
        return tuple(tuple(row) for row in self._grid)

    def inspect_cell(self, row, column):
        self._check_index(row)
        self._check_index(column)
        return self._grid[row][column]

    def inspect_row(self, index):
        self._check_index(index)
        return tuple(self._grid[index])

    def inspect_column(self, index):
        self._check_index(index)
        return tuple(self._grid[row][index] for row in range(9))

    def inspect_box(self, index):
        self._check_index(index)

        start_row = (index // 3) * 3
        start_col = (index % 3) * 3

        return tuple(
            self._grid[row][col]
            for row in range(start_row, start_row + 3)
            for col in range(start_col, start_col + 3)
        )

    def _conflicts(self, row, column, digit):
        if digit in self.inspect_row(row):
            return True

        if digit in self.inspect_column(column):
            return True

        box_index = (row // 3) * 3 + column // 3
        return digit in self.inspect_box(box_index)

    def place(self, row: int, column: int, digit: int) -> BoardResult:
        if not self._valid_index(row) or not self._valid_index(column):
            return BoardResult(False, "INVALID_COORDINATE", self.revision)

        if type(digit) is not int or digit not in self.DIGITS:
            return BoardResult(False, "INVALID_DIGIT", self.revision)

        if (row, column) in self._givens:
            return BoardResult(False, "GIVEN_CELL", self.revision)

        if self._grid[row][column] != 0:
            return BoardResult(False, "OCCUPIED_CELL", self.revision)

        if self._conflicts(row, column, digit):
            return BoardResult(False, "CONFLICT", self.revision)

        self._grid[row][column] = digit
        self._history.append((row, column, 0))
        self.revision += 1

        return BoardResult(True, "OK", self.revision)

    def undo(self) -> BoardResult:
        if not self._history:
            return BoardResult(False, "EMPTY_HISTORY", self.revision)

        row, column, old_value = self._history.pop()
        self._grid[row][column] = old_value
        self.revision += 1

        return BoardResult(True, "OK", self.revision)

    def validate_complete(self) -> bool:
        if any(0 in row for row in self._grid):
            return False

        if any(self._grid[row][col] == 0
               for row, col in self._givens):
            return False

        return all(
            set(self.inspect_row(index)) == self.DIGITS
            and set(self.inspect_column(index)) == self.DIGITS
            and set(self.inspect_box(index)) == self.DIGITS
            for index in range(9)
        )
