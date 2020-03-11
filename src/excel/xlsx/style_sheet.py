from typing import Dict, Optional
from .xmlutils import XmlElement, try_parse, NoneElement, GenericElement
from .style import Style


class StyleSheet(XmlElement):
    def __init__(self, element: XmlElement) -> None:
        super().__init__(element)

        self._numfmts = NoneElement
        self._fonts = NoneElement
        self._fills = NoneElement
        self._borders = NoneElement
        self._cellxfs = NoneElement

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

        if self._numfmts is NoneElement:
            self._numfmts = XmlElement.new('numFmts')
            self.insert(0, self._numfmts)
        if self._fonts is NoneElement:
            self._fonts = XmlElement.new('fonts')
            self.insert(1, self._fonts)
        if self._fills is NoneElement:
            self._fills = XmlElement.new('fills')
            self.insert(2, self._fills)
        if self._borders is NoneElement:
            self._borders = XmlElement.new('borders')
            self.insert(3, self._borders)
        if self._cellxfs is NoneElement:
            self._cellxfs = XmlElement.new('cellXfs')
            self.insert(4, self._cellxfs)

        for elem in [self._numfmts, self._fonts, self._fills,
         self._borders, self._cellxfs]:
            elem.remove_attrib('count')
        
        self._number_format_code_by_id: Dict[int, str] = {}
        self._number_format_id_by_code: Dict[str, int] = {}
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
            if id is not None and code:
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
        self._numfmts.append(elem)

        return id

    def create_style(self, source_id: int) -> Style:
        font: Optional[XmlElement] = None
        fill: Optional[XmlElement] = None
        border: Optional[XmlElement] = None
        xf: Optional[XmlElement] = None
        if source_id >= 0:
            source_xf = self._cellxfs[source_id]
            xf = source_xf.deepcopy()
            if source_xf.get_attrib_value('applyFont'):
                font_id = try_parse(int, source_xf.get_attrib_value('fontId'))
                if font_id is not None:
                    font = self._fonts[font_id].deepcopy()
            if source_xf.get_attrib_value('applyFill'):
                fill_id = try_parse(int, source_xf.get_attrib_value('fillId'))
                if fill_id is not None:
                    fill = self._fills[fill_id].deepcopy()
            if source_xf.get_attrib_value('applyBorder'):
                border_id = try_parse(int, source_xf.get_attrib_value('borderId'))
                if border_id is not None:
                    border = self._borders[border_id].deepcopy()
        if font is None:
            font = XmlElement.new('font')
        self._fonts.append(font)
        if fill is None:
            fill = XmlElement.new('fill')
        self._fills.append(fill)
        if border is None:
            border = XmlElement.new('border')
            border.append(XmlElement.new('left'))
            border.append(XmlElement.new('right'))
            border.append(XmlElement.new('top'))
            border.append(XmlElement.new('bottom'))
            border.append(XmlElement.new('diagonal'))
        self._borders.append(border)
        if xf is None:
            xf = XmlElement.new('xf')
        xf.put_attrib({
            'fontId': f'{len(self._fonts) - 1}',
            'fillId': f'{len(self._fills) - 1}',
            'borderId': f'{len(self._borders) - 1}',
            'applyFont': '1',
            'applyFill': '1',
            'applyBorder': '1'
        })
        self._cellxfs.append(xf)
        return Style(self, len(self._cellxfs) - 1, xf, font, fill, border)


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