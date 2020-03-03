from typing import Dict, Optional
from .xmlutils import XmlElement, try_parse, AnyStr
from lxml.etree import _Element


class StyleSheet(XmlElement):

    def __init__(self, element: _Element) -> None:
        super().__init__(element)

        self._numfmts: Optional[XmlElement] = None
        self._fonts: Optional[XmlElement] = None
        self._fills: Optional[XmlElement] = None
        self._borders: Optional[XmlElement] = None
        self._cellxfs: Optional[XmlElement] = None

        for child in self:
            name = child.tag.localname
            if name == 'numFmts':
                self._numfmts = child
            elif name == 'fonts':
                self._fonts = child
            elif name == 'fills':
                self._fills = child
            elif name == 'borders':
                self._borders = child
            elif name == 'cellXfs':
                self._cellxfs = child

        if self._numfmts is None:
            self.insert(0, XmlElement.new('numFmts'))

        for elem in [self._numfmts, self._fonts, self._fills,
         self._borders, self._cellxfs]:
            if elem:
                elem.remove_attrib('count')
        
        self._number_format_code_by_id: Dict[int, AnyStr] = {}
        self._number_format_id_by_code: Dict[AnyStr, int] = {}
        self._next_number_format_id = starting_custom_number_format_id
        self._cache_number_formats()

    def _cache_number_formats(self):
        for id in standard_codes:
            code = standard_codes[id]
            self._number_format_code_by_id[id] = code
            self._number_format_id_by_code[code] = id
        
        self._next_number_format_id = starting_custom_number_format_id

        for child in self._numfmts:
            id = try_parse(int, child.get_attrib_value('numFmtId'))
            code = child.get_attrib_value('formatCode')
            if id and code:
                self._number_format_code_by_id[id] = code
                self._number_format_id_by_code[code] = id
                if id >= self._next_number_format_id:
                    self._next_number_format_id = id + 1

    def get_number_format_code(self, id: int):
        return self._number_format_code_by_id[id]

    def get_number_format_id(self, code: str):
        if code in self._number_format_id_by_code:
            return self._number_format_id_by_code[code]
        
        id = self._next_number_format_id + 1
        self._number_format_code_by_id[id] = code
        self._number_format_id_by_code[code] = id

        elem = XmlElement.new('numFmt')
        elem.attrib['numFmtId'] = f'{id}'
        elem.attrib['formatCode'] = code
        self.append(elem)

        return id

    


starting_custom_number_format_id = 164

standard_codes: Dict[int, str] = {
    0: 'General',
    1: '0',
    2: '0.00',
    3: '#,##0',
    4: '#,##0.00',
    9: '0%',
    10: '0.00%',
    11: '0.00E+00',
    12: '# ?/?',
    13: '# ??/??',
    14: 'mm-dd-yy',
    15: 'd-mmm-yy',
    16: 'd-mmm',
    17: 'mmm-yy',
    18: 'h:mm AM/PM',
    19: 'h:mm:ss AM/PM',
    20: 'h:mm',
    21: 'h:mm:ss',
    22: 'm/d/yy h:mm',
    37: '#,##0 ;(#,##0)',
    38: '#,##0 ;[Red](#,##0)',
    39: '#,##0.00;(#,##0.00)',
    40: '#,##0.00;[Red](#,##0.00)',
    45: 'mm:ss',
    46: '[h]:mm:ss',
    47: 'mmss.0',
    48: '##0.0E+0',
    49: '@'
  }