from typing import *
from .third_party.xlrd import open_workbook
from .third_party.xlutils.copy import copy
from .third_party.xlwt import Worksheet as _Worksheet


class Worksheet():
    def __init__(self, sheet: _Worksheet):
        self._sheet: _Worksheet = sheet

    def copy_row_to(self, copy_index: int, to_index: int):
        row = self._sheet.insert_row(to_index)
        self._sheet.copy_row_style(copy_index, to_index)
        return row

    def update(self, row: int, column: int, value: Any):
        self._sheet.update(row, column, value)


class Workbook():
    def __init__(self, filename: str):
        self._workbook = copy(open_workbook(filename, formatting_info=1))

    def get_sheet(self, index: int) -> Worksheet:
        return Worksheet(self._workbook.get_sheet(index))

    def save(self, filename: str):
        self._workbook.save(filename)

