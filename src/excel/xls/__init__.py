from typing import *
from .third_party.xlrd import open_workbook
from .third_party.xlutils.copy import copy
from .third_party.xlwt import Worksheet as _Worksheet, Row as _Row
from ..xlsx.address_converter import CellRef, column_name_to_number

class Row:
    def __init__(self, row: _Row):
        self._row = row

    def update(self, column: Union[int, str], value: Any):
        if isinstance(column, str):
            column = column_name_to_number(column)
        self._row.update(column - 1, value)

    def value(self, column: Union[int, str]):
        if isinstance(column, str):
            column = column_name_to_number(column)
        return self._row.value(column - 1)


class Worksheet:
    def __init__(self, sheet: _Worksheet):
        self._sheet: _Worksheet = sheet

    def insert_row_copy_style(self, copy_index: int, to_index: int):
        row = self._sheet.insert_row(to_index - 1)
        self._sheet.copy_row_style(copy_index - 1, to_index - 1)
        return Row(row)

    def copy_row(self, from_index: int, to_index: int):
        return Row(self._sheet.copy_row(from_index - 1, to_index - 1))

    def update(self, row: int, column: Union[int, str], value: Any):
        if isinstance(column, str):
            column = column_name_to_number(column)
        self._sheet.update(row - 1, column - 1, value)

    def row(self, index: int):
        return Row(self._sheet.row(index - 1))

    def value(self, row: int, column: Union[int, str]):
        if isinstance(column, str):
            column = column_name_to_number(column)
        return self._sheet.row(row - 1).value(column - 1)


class Workbook():
    def __init__(self, filename: str):
        self._workbook = copy(open_workbook(filename, formatting_info=1))

    def get_sheet(self, index: int) -> Worksheet:
        return Worksheet(self._workbook.get_sheet(index))

    def save(self, filename: str):
        self._workbook.save(filename)

