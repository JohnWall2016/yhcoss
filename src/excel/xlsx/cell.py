import re
from typing import Optional, Dict, TypeVar, Union, List, Type, Any

from .formula_error import FormulaError
from .shared_strings import RichText
from .xmlutils import XmlElement, XmlName, try_parse
from .address_converter import CellRef
from .xmlutils import XmlElement

import src.excel.xlsx.workbook as wb
import src.excel.xlsx.sheet as st
import src.excel.xlsx.row as rw

T = TypeVar('T')

class Cell:
    def __init__(self, row: 'rw.Row', element_or_column_index: Union[XmlElement, int], style_id: int = None):
        self._row = row
        #self._column_index: Optional[int] = None
        self._style_id: Optional[int] = None
        self._remaining_attrib: Dict[str, str] = {}
        self._type: Optional[str] = None
        self._value: Optional[Union[str, RichText, bool, FormulaError, int, float]] = None
        self._forumla_type: Optional[str] = None
        self._forumla_ref: Optional[str] = None
        self._shared_formula_id: Optional[int] = None
        self._remaning_formula_attrib: Dict[str, str] = {}
        self._formula: Optional[str] = None
        self._remaning_children: Optional[List[XmlElement]] = None

        if isinstance(element_or_column_index, XmlElement):
            self._parse(element_or_column_index)
        else:
            self._column_index = element_or_column_index
            self._style_id = style_id

    @property
    def row(self) -> 'rw.Row':
        return self._row

    @property
    def sheet(self) -> 'st.Sheet':
        return self._row.sheet

    @property
    def workbook(self) -> 'wb.Workbook':
        return self._row.sheet.workbook

    @property
    def row_index(self) -> int:
        return self._row.index

    @property
    def column_index(self) -> int:
        return self._column_index

    @property
    def address(self) -> str:
        return CellRef(self.row_index, self.column_index).to_address()

    def get_value(self, cls: Type[T] = str) -> Optional[T]:
        if self._value is None:
            return None
        elif isinstance(self._value, cls):
            return self._value
        elif cls == str:
            return str(self._value)
        elif cls == float and not isinstance(self._value, FormulaError):
            val = self._value
            if isinstance(val, RichText):
                val = str(val)
            return float(val)
        elif cls == int and not isinstance(self._value, FormulaError):
            val = self._value
            if isinstance(val, RichText):
                val = str(val)
            return int(val)
        return None

    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, value: Any):
        self._value = value

    def _parse(self, element: XmlElement):
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

        # Parse the value
        if self._type == 's':
            elem = element.find_by_localname('v')
            if elem is not None and elem.text:
                shared_index = int(elem.text)
                self._value = self.workbook.shared_strings.get_string_by_index(shared_index)
        elif self._type == 'str':
            elem = element.find_by_localname('v')
            if elem is not None:
                self._value = elem.text
        elif self._type == 'inlineStr':
            is_ = element.find_by_localname('is')
            if is_: # is_ is Not None and len(is_) > 0
                t = is_[0]
                if t.tag.localname == 't':
                    self._value = t.text
                else:
                    self._value = RichText(is_)
        elif self._type == 'b':
            elem = element.find_by_localname('v')
            if elem is not None:
                self._value = elem.text == '1'
        elif self._type == 'e':
            elem = element.find_by_localname('v')
            if elem is not None and elem.text:
                self._value = FormulaError(elem.text)
        else:
            elem = element.find_by_localname('v')
            if elem is not None and elem.text:
                if re.match(r'^\d+$', elem.text):
                    self._value = int(elem.text)
                elif re.match(r'^\d+\.\d+$', elem.text):
                    self._value = float(elem.text)

        # Parse the formula
        elem = element.find_by_localname('f')
        if elem is not None:
            for k, v in elem.attrib:
                localname = XmlName(k).localname
                if localname == 't':
                    self._forumla_type = v or 'normal'
                elif localname == 'ref':
                    self._forumla_ref = v
                elif localname == 'si':
                    self._shared_formula_id = try_parse(int,v)
                    if self._shared_formula_id is not None:
                        self.sheet.update_max_shared_formula_id(self._shared_formula_id)
                else:
                    self._remaning_formula_attrib[k] = v
            self._formula = elem.text

        element.remove('f')
        element.remove('v')
        element.remove('is')

        self._remaning_children = [e for e in element]

    def to_xml(self, clear_value: bool = False) -> XmlElement:
        elem = XmlElement.new('c', self._remaining_attrib)
        address = self.address
        if address:
            elem.attrib['r'] = address
        if self._forumla_type:
            f = XmlElement.new('f', self._remaning_formula_attrib)
            attrib: Dict[Union[str, XmlName], Optional[str]] = {}
            if self._forumla_type and self._forumla_type != 'normal':
                attrib['t'] = self._forumla_type
            if self._forumla_ref:
                attrib['ref'] = self._forumla_ref
            if self._shared_formula_id:
                if self._shared_formula_id:
                    attrib['si'] = str(self._shared_formula_id)
                else:
                    attrib['si'] = None
            f.put_attrib(attrib)
            if self._formula:
                f.text = self._formula
            elem.append(f)
        elif not clear_value and self._value is not None:
            type_: Optional[str] = None
            text: str = ''
            if self._type == 's' or isinstance(self._value, str) or isinstance(self._value, RichText):
                type_ = 's'
                text = str(self.workbook.shared_strings.get_index_from_string(str(self._value)))
            elif isinstance(self._value, bool):
                type_ = 'b'
                text = '1' if self._value else '0'
            elif isinstance(self._value, int) or isinstance(self._value, float):
                type_ = ''
                text = str(self._value)
            if type_ is not None:
                if type_:
                    elem.attrib['t'] = type_
                subelem = XmlElement.new('v')
                subelem.text = text
                elem.append(subelem)
        if self._style_id is not None:
            elem.attrib['s'] = str(self._style_id)
        if self._remaning_children:
            for c in self._remaning_children:
                elem.append(c.deepcopy())
        return elem

