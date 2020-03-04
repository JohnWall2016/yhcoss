from typing import Optional, Dict
from .xmlutils import XmlElement, XmlName
from .row import Row
from .address_converter import CellRef
from .xmlutils import XmlElement


class Cell:
    def __init__(self, row: Row, element: XmlElement):
        self._row = row
        self._column_index: Optional[int] = None
        self._style_id: Optional[int] = None
        self._remaining_attrib: Dict[str, str] = {}
        self._type: Optional[str] = None

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
            # TODO:
            pass
