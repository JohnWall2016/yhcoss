from zipfile import ZipFile

from lxml.etree import QName, XML, ElementTree
from typing import *
from .xmlutils import XmlElement, GenericElement


class Workbook(XmlElement):
    def __init__(self, element: GenericElement[str]):
        super().__init__(element)
        self._max_sheet_id: int = 0

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

            wb = Workbook(get_xml('xl/workbook.xml'))
            wb._init(get_xml)
            return wb

    def _init(self, get_xml: Callable[[str], GenericElement[str]]):
        pass