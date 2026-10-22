"""Black-box cases from specs/board_contract.md."""
import pytest
from src.board import Board
from .conftest import SOLVED


def test_constructor_defensively_copies_input(puzzle):
    board = Board(puzzle)
    puzzle[0][0] = 0
    assert board.inspect_cell(0, 0) == 5

@pytest.mark.parametrize('bad', [[], [[0]*9]*8, [[0]*8]*9, [[True]+[0]*8]+[[0]*9]*8, [[10]+[0]*8]+[[0]*9]*8])
def test_constructor_rejects_malformed_boards(bad):
    with pytest.raises(ValueError):
        Board(bad)

def test_constructor_rejects_conflicting_givens(puzzle):
    puzzle[0][2] = 5
    with pytest.raises(ValueError):
        Board(puzzle)

def test_inspect_views_and_revision_do_not_mutate(puzzle):
    board = Board(puzzle)
    initial = board.revision
    assert len(board.inspect_board()) == 9
    assert board.inspect_row(0)[0] == 5
    assert board.inspect_column(0)[0] == 5
    assert board.inspect_box(0)[0] == 5
    assert board.revision == initial

def test_valid_placement_advances_revision(puzzle):
    board = Board(puzzle)
    result = board.place(0, 2, 4)
    assert result.accepted is True
    assert board.inspect_cell(0, 2) == 4
    assert board.revision == 1

def test_invalid_coordinate_rejects_without_effect(puzzle):
    board = Board(puzzle)
    before = board.inspect_board()
    result = board.place(-1, 2, 4)
    assert result.accepted is False and result.reason == 'INVALID_COORDINATE'
    assert board.inspect_board() == before and board.revision == 0

def test_invalid_digit_rejects_without_effect(puzzle):
    board = Board(puzzle)
    result = board.place(0, 2, 10)
    assert result.accepted is False and result.reason == 'INVALID_DIGIT'
    assert board.inspect_cell(0, 2) == 0 and board.revision == 0

def test_given_cell_cannot_be_changed(puzzle):
    board = Board(puzzle)
    result = board.place(0, 0, 1)
    assert result.accepted is False and result.reason == 'GIVEN_CELL'
    assert board.inspect_cell(0, 0) == 5

@pytest.mark.parametrize('row,col,digit', [(0,2,3), (0,2,8), (0,2,9)])
def test_row_column_or_box_conflict_is_rejected(puzzle,row,col,digit):
    board = Board(puzzle)
    before = board.inspect_board()
    result = board.place(row,col,digit)
    assert result.accepted is False and result.reason == 'CONFLICT'
    assert board.inspect_board() == before and board.revision == 0

def test_occupied_cell_rejected(puzzle):
    board = Board(puzzle)
    assert board.place(0,2,4).accepted
    result = board.place(0,2,1)
    assert result.accepted is False and result.reason == 'OCCUPIED_CELL'
    assert board.inspect_cell(0,2) == 4 and board.revision == 1

def test_undo_restores_latest_accepted_placement(puzzle):
    board = Board(puzzle)
    assert board.place(0,2,4).accepted
    assert board.place(0,3,6).accepted
    assert board.undo().accepted
    assert board.inspect_cell(0,3) == 0
    assert board.inspect_cell(0,2) == 4
    assert board.revision == 3

def test_empty_undo_is_nonmutating(puzzle):
    board = Board(puzzle)
    result = board.undo()
    assert result.accepted is False and result.reason == 'EMPTY_HISTORY'
    assert board.revision == 0

def test_incomplete_board_fails_validation(puzzle):
    assert Board(puzzle).validate_complete() is False

def test_solved_board_passes_validation():
    assert Board(SOLVED).validate_complete() is True
