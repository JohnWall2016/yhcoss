from .cell import Cell


class Range:
    def __init__(self, start_cell: Cell, end_cell: Cell):
        self.start_cell = start_cell
        self.end_cell = end_cell
        # TODO: