from zipfile import ZipFile

from lxml.etree import QName, XML, ElementTree
from typing import *
from .xmlutils import XmlElement, GenericElement, try_parse, try_parse_default
from .shared_strings import SharedStrings
from .sheet import Sheet
from .content_types import ContentTypes
from .app_properties import AppProperties
from .core_properties import CoreProperties
from .relationships import Relationships
from .style_sheet import StyleSheet


class Workbook(XmlElement):
    def __init__(self, element: XmlElement,
                 get_xml: Callable[[str], Optional[XmlElement]]):
        super().__init__(element)
        self._max_sheet_id: int = 0
        self._sheets: List[Sheet] = []

        elem = get_xml('[Content_Types].xml')
        if elem is not None:
            self._content_types = ContentTypes(elem)

        elem = get_xml('docProps/app.xml')
        if elem is not None:
            self._app_properties = AppProperties(elem)

        elem = get_xml('docProps/core.xml')
        if elem is not None:
            self._core_properties = CoreProperties(elem)

        elem = get_xml('xl/_rels/workbook.xml.rels')
        self._relationships = Relationships(elem)

        elem = get_xml('xl/sharedStrings.xml')
        self._shared_strings = SharedStrings(elem)

        elem = get_xml('xl/styles.xml')
        if elem is not None:
            self._style_sheet = StyleSheet(elem)

        if self._relationships.find_by_type('sharedStrings') is None:
            self._relationships.add('sharedStrings', 'sharedStrings.xml')

        if self._content_types.find_by_part_name('/xl/sharedStrings.xml') is None:
            self._content_types.add('/xl/sharedStrings.xml', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml')

        self._sheets_elem = self.find_by_localname('sheets')
        if self._sheets_elem is not None:
            for i in range(0, len(self._sheets_elem)):
                sheet_id_elem = self._sheets_elem[i]
                sheet_id = sheet_id_elem.get_attrib_value('sheetId')
                if sheet_id:
                    sheet_id = try_parse_default(int, sheet_id, -1)
                    if sheet_id > self._max_sheet_id:
                        self._max_sheet_id = sheet_id
                sheet_elem = get_xml(f'xl/worksheets/sheet{i + 1}.xml')
                sheet_relationships_elem = get_xml(f'xl/worksheets/_rels/sheet{i + 1}.xml.rels')
                self._sheets.append(Sheet(self, sheet_id_elem, sheet_elem, sheet_relationships_elem))


    @staticmethod
    def from_file(filename: str):
        with ZipFile(filename) as archive:

            def get_xml(path: str) -> Optional[XmlElement]:
                nonlocal archive
                if not archive.NameToInfo.get(path):
                    return None
                elem = XML(archive.read(path))
                if (isinstance(elem.tag, bytes) or (isinstance(elem.tag, QName) and 
                                                    isinstance(elem.tag.localname, bytes))):
                     raise Exception('Must be Unicode xml file')
                return XmlElement(ElementTree(cast(GenericElement[str], elem)).getroot())

            wb_elem = get_xml('xl/workbook.xml')
            if wb_elem is None:
                raise Exception('Cannot read \'xl/workbook.xml\'')
            wb = Workbook(wb_elem, get_xml)
            return wb

    @property
    def shared_strings(self) -> SharedStrings:
        return self._shared_strings

    