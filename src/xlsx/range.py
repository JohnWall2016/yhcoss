from src.xlsx.address_converter import RangeRef
from .cell import Cell


class Range:
    def __init__(self, start_cell: Cell, end_cell: Cell):
        self._start_cell = start_cell
        self._end_cell = end_cell
        self._find_range_extent()

    @property
    def sheet(self):
        return self._start_cell.sheet
        
    def _find_range_extent(self):
        self._min_row_index = min(self._start_cell.row_index, self._end_cell.row_index)
        self._max_row_index = max(self._start_cell.row_index, self._end_cell.row_index)
        self._min_column_index = min(self._start_cell.column_index, self._end_cell.column_index)
        self._max_column_index = max(self._start_cell.column_index, self._end_cell.column_index)
        self._num_rows = self._max_row_index - self._min_row_index + 1
        self._num_columns = self._max_column_index - self._min_column_index + 1
        
    def address(self,
                anchored: bool = False,
                start_row_anchored: bool = False,
                start_column_anchored: bool = False,
                end_row_anchored: bool = False,
                end_column_anchored: bool = False,
                include_sheet_name: bool = False) -> str:
        range = RangeRef(self._start_cell.row_index,
                         self._start_cell.column_index,
                         self._end_cell.row_index,
                         self._end_cell.column_index,
                         anchored,
                         start_row_anchored,
                         start_column_anchored,
                         end_row_anchored)
        address = ''
        if include_sheet_name and self.sheet.name:
            address += "'" + self.sheet.name.replace("'", "''") + "'!"
        address += range.to_address()
        return address