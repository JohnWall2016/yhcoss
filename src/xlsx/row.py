from copy import deepcopy
from src.xlsx.address_converter import column_name_to_number
from typing import Optional, Union, Dict
from .workbook import Workbook
from .cell import Cell
from .sheet import Sheet
from .xmlutils import XmlElement, try_parse


class Row(XmlElement):
    def __init__(self, sheet: Sheet, element: XmlElement):
        super().__init__(element)
        self._sheet = sheet
        r = self.get_attrib_value('r')
        idx = int(r) if r else None
        if idx is None:
            raise Exception('Row index cannot be None')
        self._index = idx
        self._cells: Dict[int, Cell] = {}
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
    def index(self) -> int:
        return self._index

    def __len__(self) -> int:
        return len(self._cells)

    def __getitem__(self, column_index: int) -> Cell:
        return self._cells[column_index]

    def __contain__(self, column_index: int) -> bool:
        return column_index in self._cells

    def get(self, column_index_or_name: Union[int, str]) -> Optional[Cell]:
        if isinstance(column_index_or_name, str):
            column_index_or_name = column_name_to_number(column_index_or_name)        
        return self._cells.get(column_index_or_name)

    def to_xml(self, row_index: int = None, clear_value: bool = False) -> XmlElement:
        self.clear()
        elem = deepcopy(self)
        if row_index:
            elem.attrib['r'] = str(row_index)
        for c in sorted(self._cells):
            elem.append(self._cells[c].to_xml())
        return elem
