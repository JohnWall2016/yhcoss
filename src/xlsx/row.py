from typing import Optional
from .workbook import Workbook
from .cell import Cell
from .sheet import Sheet
from .xmlutils import XmlElement, try_parse
from collections import OrderedDict


class Row(XmlElement):
    def __init__(self, sheet: Sheet, element: XmlElement):
        super().__init__(element)
        self._sheet = sheet
        r = self.get_attrib_value('r')
        self._index = try_parse(int, r) if r else None
        self._cells: OrderedDict[int, Cell] = OrderedDict()
        for c in self:
            cell = Cell(self, c)
            if cell.column_index:
                self._cells[cell.column_index] = cell

    @property
    def sheet(self) -> Sheet:
        return self._sheet

    @property
    def workbook(self) -> Workbook:
        return self._sheet.workbook

    @property
    def index(self) -> Optional[int]:
        return self._index
