from .workbook import Workbook
from typing import Optional, Dict
from .xmlutils import XmlElement, XmlName
from .row import Row
from .address_converter import CellRef
from .xmlutils import XmlElement
from .sheet import Sheet


class Cell:
    def __init__(self, row: Row, element: XmlElement):
        self._row = row
        self._column_index: Optional[int] = None
        self._style_id: Optional[int] = None
        self._remaining_attrib: Dict[str, str] = {}
        self._type: Optional[str] = None
        self._value = None

    @property
    def row(self) -> Row:
        return self._row

    @property
    def sheet(self) -> Sheet:
        return self._row.sheet

    @property
    def workbook(self) -> Workbook:
        return self._row.sheet.workbook

    @property
    def column_index(self) -> Optional[int]:
        return self._column_index

    def _parse_node(self, element: XmlElement):
        for name, value in element.attrib.items():
            localname = XmlName(name).localname
            if localname == 'r':
                ref = CellRef.from_address(value)
                self._column_index = ref.column
            elif localname == 's':
                self._style_id = int(value)
            elif localname == 't':
                self._type = value
            else:
                self._remaining_attrib[name] = value

        if self._type == 's':
            elem = element.find_by_localname('v')
            if elem and elem.text:
                shared_index = int(elem.text)
                self._value = self.workbook.shared_strings.get_string_by_index(shared_index)
            # TODO
