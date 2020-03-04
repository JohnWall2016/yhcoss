from typing import Final, Optional, Union
import re

from re import match


_cell_regex: Final = r'(\$?)([A-Z]+)(\$?)(\d+)'
_range_regex: Final = f'({_cell_regex}):({_cell_regex})'


class CellRef:
    def __init__(self, row: int, column: int,
                 column_name: str = None,
                 anchored: bool = False,
                 row_anchored: bool = False,
                 column_anchored: bool = False):
        self._row = row
        self._column = column
        self._row_anchored = anchored or row_anchored
        self._column_anchored = anchored or column_anchored
        self._column_name = column_name or column_number_to_name(self._column)

    @staticmethod
    def from_address(address: str) -> Optional['CellRef']:
        m = re.match(_cell_regex, address)
        if m:
            return CellRef(row = int(m.group(4)),
                           column = column_name_to_number(m.group(2)),
                           column_name = m.group(2),
                           row_anchored = m.group(3) != '',
                           column_anchored = m.group(1) != '')
        else:
            return None

    def to_address(self) -> str:
        address = ''
        if self._column_anchored:
            address += '$'
        address += self._column_name
        if self._row_anchored:
            address += '$'
        address += f'{self._row}'
        return address


class RangeRef:
    def __init__(self,
                 start_row_or_start_cell: Optional[Union[int, CellRef]], 
                 start_column_or_end_cell: Optional[Union[int, CellRef]],
                 end_row: Optional[int] = None, 
                 end_column :Optional[int] = None,
                 anchored = False, 
                 start_row_anchored = False,
                 start_column_anchored = False,
                 end_row_anchored = False,
                 end_column_anchored = False):
        if (isinstance(start_row_or_start_cell, int) and 
            isinstance(start_column_or_end_cell, int) and
            isinstance(end_row, int) and isinstance(end_column, int)):
            self._start = CellRef(start_row_or_start_cell, start_column_or_end_cell,
                                anchored = anchored,
                                row_anchored = start_row_anchored,
                                column_anchored = start_column_anchored)
            self._end = CellRef(end_row, end_column,
                                anchored = anchored,
                                row_anchored = end_row_anchored,
                                column_anchored = end_column_anchored)
        elif (isinstance(start_row_or_start_cell, CellRef) and 
              isinstance(start_column_or_end_cell, CellRef)):
            self._start = start_row_or_start_cell
            self._end = start_column_or_end_cell
        else:
            raise Exception('The first and second arguments must both be int or CellRef')

    @staticmethod
    def from_address(address: str) -> Optional['RangeRef']:
        m = re.match(_range_regex, address)
        if m:
            return RangeRef(CellRef.from_address(m.group(1)),
                            CellRef.from_address(m.group(6)))
        else:
            return None
        
        
def column_number_to_name(number: int):
    dividend = number
    name = ''
    modulo = 0
    while dividend > 0:
        modulo = (dividend - 1) % 26
        name = chr(65 + modulo) + name
        dividend = (dividend - modulo) // 26
    return name


def column_name_to_number(name: str):
    name = name.upper()
    sum = 0
    for c in name:
        sum *= 26
        sum += ord(c) - 64
    return sum