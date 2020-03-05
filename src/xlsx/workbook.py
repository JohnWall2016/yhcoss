from zipfile import ZipFile

from lxml.etree import QName, XML, ElementTree
from typing import *
from .xmlutils import XmlElement, GenericElement
from .shared_strings import SharedStrings
from .sheet import Sheet
from .content_types import ContentTypes
from .app_properties import AppProperties
from .core_properties import CoreProperties
from .relationships import Relationships
from .style_sheet import StyleSheet


class Workbook(XmlElement):
    def __init__(self, element: GenericElement[str],
                 get_xml: Callable[[str], GenericElement[str]]):
        super().__init__(element)
        self._max_sheet_id: int = 0
        self._sheets: List[Sheet] = []

        self._content_types = ContentTypes(get_xml('[Content_Types].xml'))
        self._app_properties = AppProperties(get_xml('docProps/app.xml'))
        self._core_properties = CoreProperties(get_xml('docProps/core.xml'))
        self._relationships = Relationships(get_xml('xl/_rels/workbook.xml.rels'))
        self._shared_strings = SharedStrings(get_xml('xl/sharedStrings.xml'))
        self._style_sheet = StyleSheet(get_xml('xl/styles.xml'))

    @staticmethod
    def from_file(filename: str):
        with ZipFile(filename) as archive:

            def get_xml(path: str):
                nonlocal archive
                elem = XML(archive.read(path))
                if (isinstance(elem.tag, bytes) or 
                    (isinstance(elem.tag, QName) and 
                     isinstance(elem.tag.localname, bytes))):
                     raise Exception('Must be Unicode xml file')
                return ElementTree(
                    cast(GenericElement[str], elem)).getroot()

            wb = Workbook(get_xml('xl/workbook.xml'), get_xml)
            return wb

    @property
    def shared_strings(self) -> SharedStrings:
        return self._shared_strings