from .address_converter import column_name_to_number
from typing import Dict
from .workbook import *
from .cell import Cell
from .sheet import *
from .xmlutils import XmlElement


class Row(XmlElement):
    def __init__(self, sheet: 'Sheet', element: XmlElement):
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
            self._cells[cell.column_index] = cell

    @property
    def sheet(self) -> 'Sheet':
        return self._sheet

    @property
    def workbook(self) -> 'Workbook':
        return self._sheet.workbook

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int):
        self._index = value
        self.attrib['r'] = str(value)

    def __len__(self) -> int:
        return len(self._cells)

    def __getitem__(self, index: int) -> Cell:
        if index in self._cells:
            return self._cells[index]

        s = self.get_attrib_value('s')
        row_style_id = try_parse(int, s) if s else None
        column_style_id = self.sheet.existing_column_style_id(index)

        style_id = None
        if row_style_id is not None:
            style_id = row_style_id
        elif column_style_id is not None:
            style_id = column_style_id

        cell = Cell(self, index, style_id)
        self._cells[index] = cell
        
        return cell

    def cell(self, name: str) -> Cell:
        index = column_name_to_number(name)        
        return self[index]

    def to_xml(self, row_index: int = None, clear_value: bool = False) -> XmlElement:
        self.clear()
        elem = self.deepcopy()
        if row_index is not None:
            elem.attrib['r'] = str(row_index)
        for c in sorted(self._cells):
            elem.append(self._cells[c].to_xml())
        return elem
