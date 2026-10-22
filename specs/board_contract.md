# Board public contract (V1)

## Representation

`Board(givens: Sequence[Sequence[int]])` accepts exactly 9 rows of 9 **true integers** in 0..9 (0 means blank), rejecting malformed shapes, invalid digits and duplicate nonzero givens in any row, column or box with `ValueError`. The initial grid and clue mask are copied defensively. No caller receives writable internal references.

## Inspection

`inspect_board() -> tuple[tuple[int,...],...]`; `inspect_cell(row,column) -> int`; `inspect_row(index)`, `inspect_column(index)`, `inspect_box(index) -> tuple[int,...]`. Box indices 0..8 enumerate left-to-right, top-to-bottom. Invalid indices return structured `INVALID_COORDINATE` through tool dispatch (board methods may raise `ValueError`; adapter maps it). Reads never mutate revision.

## Placement

`place(row:int,column:int,digit:int) -> BoardResult` accepts only a currently empty, non-given cell with digit 1..9 that does not duplicate a digit in its row, column or 3×3 box. On success: writes digit, pushes `(row,column,old_value=0)` onto LIFO undo history, increments revision by 1, returns `accepted=True`. Rejections: `INVALID_COORDINATE`, `INVALID_DIGIT`, `GIVEN_CELL`, `OCCUPIED_CELL`, `CONFLICT`; board, history, revision unchanged.

## Undo

`undo() -> BoardResult` pops only the most recent **accepted placement**, restores its previous value (0), increments revision by 1, returns `accepted=True`. With empty history returns `EMPTY_HISTORY` and changes nothing. Undo cannot alter given clues. Rejected actions never appear in history. Revisions are monotonic and never roll back.

## Completion

`validate_complete() -> bool` returns true iff all 81 cells are nonzero, all original clues remain intact, and every row, column and box contains exactly digits 1..9. It does not mutate state. `submit` never trusts a model's claim of correctness.

## Derived black-box tests (to write in commit 2)

Valid placement advances revision; invalid coordinate and digit preserve board; given clue is immutable; row/column/box conflicts reject without side effects; occupied mutable cell rejects; undo restores last placement and increments revision; undo with empty stack is non-mutating; incomplete board fails validation; solved board passes validation.
