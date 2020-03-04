from zipfile import ZipFile
from lxml.etree import _Element, XML, ElementTree
from typing import *
from .xmlutils import XmlElement


class Workbook(XmlElement):
    def __init__(self, element: _Element[str]):
        super().__init__(element)
        self._max_sheet_id: int = 0

    @staticmethod
    def from_file(filename: str):
        with ZipFile(filename) as archive:

            def get_xml(path: str):
                nonlocal archive
                return ElementTree(
                    XML(str(archive.read(path), 'utf-8'))).getroot()

            wb = Workbook(get_xml('xl/workbook.xml'))
            wb._init(get_xml)
            return wb

    def _init(self, get_xml: Callable[[str], _Element[str]]):
        pass