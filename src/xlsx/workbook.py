from zipfile import ZipFile
from lxml.etree import QName, XML, ElementTree
from typing import *

from .xmlutils import XmlElement, GenericElement, try_parse, try_parse_default
from .shared_strings import SharedStrings
from .content_types import ContentTypes
from .app_properties import AppProperties
from .core_properties import CoreProperties
from .relationships import Relationships
from .style_sheet import StyleSheet

from .sheet import *


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
                sheet_id = try_parse_default(int, sheet_id_elem.get_attrib_value('sheetId'), -1)
                if sheet_id > self._max_sheet_id:
                    self._max_sheet_id = sheet_id
                sheet_elem = get_xml(f'xl/worksheets/sheet{i + 1}.xml')
                sheet_relationships_elem = get_xml(f'xl/worksheets/_rels/sheet{i + 1}.xml.rels')
                self._sheets.append(Sheet(self, sheet_id_elem, sheet_elem, sheet_relationships_elem))

        self._defined_name_local_sheet: Dict[XmlElement, Sheet] = {}

        self._parse_sheet_refs()

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

    def to_data(self):
        
        def insert_archive_file(path: str, elem: XmlElement):
            print('=' * 60)
            print(f'path: {path}')
            print(elem.tostring(encoding='unicode', pretty_print=True))
            print('=' * 60)

        self._set_sheet_refs()

        defined_names_elem = self.find_by_localname('definedNames')
        for i in range(0, len(self._sheets)):
            sheet = self._sheets[i]
            if sheet.auto_filter is not None:
                if defined_names_elem is None:
                    defined_names_elem = XmlElement.new('definedNames')
                    self.insert_in_order(defined_names_elem, element_order)
                defined_name_elem = XmlElement.new('definedName',
                                                   {
                                                       'name': '_xlnm._FilterDatabase',
                                                       'localSheetId': i,
                                                       'hidden': '1'
                                                   })
                defined_name_elem.text = sheet.auto_filter.address(include_sheet_name=True, anchored=True)
                defined_names_elem.append(defined_name_elem)

        self._sheets_elem.clear()
        for i in range(0, len(self._sheets)):
            sheet = self._sheets[i]
            sheet_xmls = sheet.to_xmls()
            id = sheet_xmls['id'].get_attrib_value_local('id')
            if id:
                relationships = self._relationships.find_by_id(id)
                relationships.attrib['Target'] = f'worksheets/sheet{i + 1}.xml'
            self._sheets_elem.append(sheet_xmls['id'])
            insert_archive_file(f'xl/worksheets/sheet{i + 1}.xml', sheet_xmls['sheet'])
            relationships_elem = sheet_xmls['relationships']
            if relationships_elem is not None:
                insert_archive_file(f'xl/worksheets/_rels/sheet{i + 1}.xml.rels', relationships_elem)

        insert_archive_file('[Content_Types].xml', self._content_types)
        insert_archive_file('docProps/app.xml', self._app_properties)
        insert_archive_file('docProps/core.xml', self._core_properties)
        insert_archive_file('xl/_rels/workbook.xml.rels', self._relationships)
        insert_archive_file('xl/sharedStrings.xml', self._shared_strings)
        insert_archive_file('xl/styles.xml', self._style_sheet)
        insert_archive_file('xl/workbook.xml', self)

    def sheet(self, name: str) -> Optional[Sheet]:
        if self._sheets:
            for sheet in self._sheets:
                if sheet.name == name:
                    return sheet
        return None
    
    def __len__(self)-> int:
        return len(self._sheets)
    
    def __getitem__(self, index: int) -> Sheet:
        return self._sheets[index]

    @property
    def shared_strings(self) -> SharedStrings:
        return self._shared_strings

    def _parse_sheet_refs(self):
        book_views_elem = self.find_by_localname('bookViews')
        work_book_view_elem = book_views_elem.find_by_localname('workbookView')
        active_tab_id = try_parse_default(int, work_book_view_elem.get_attrib_value('activeTab'), 0)
        self._active_sheet = self._sheets[active_tab_id]

        defined_names_elem = self.find_by_localname('definedNames')
        if defined_names_elem:
            for defined_name_elem in defined_names_elem:
                local_sheet_id = try_parse(int, defined_name_elem.find_by_localname('localSheetId'))
                if local_sheet_id is not None:
                    self._defined_name_local_sheet[defined_name_elem] = self._sheets[local_sheet_id]
            
    def _set_sheet_refs(self):
        book_views_elem = self.find_by_localname('bookViews')
        if book_views_elem is None:
            book_views_elem = XmlElement.new('bookViews')
            self.insert_in_order(book_views_elem, element_order)

        workbook_view_elem = book_views_elem.find_by_localname('workbookView')
        if workbook_view_elem is None:
            workbook_view_elem = XmlElement.new('workbookView')
            book_views_elem.append(workbook_view_elem)

        if self._active_sheet in self._sheets:
            workbook_view_elem.attrib['activeTab'] = str(self._sheets.index(self._active_sheet))

        defined_names_elem = self.find_by_localname('definedNames')
        if defined_names_elem:
            for defined_name_elem in defined_names_elem:
                local_sheet = self._defined_name_local_sheet.get(defined_name_elem)
                if local_sheet is not None and local_sheet in self._sheets:
                    defined_name_elem.attrib['localSheetId'] = str(self._sheets.index(local_sheet))

element_order: Final = [
    "fileVersion",
    "fileSharing",
    "workbookPr",
    "workbookProtection",
    "bookViews",
    "sheets",
    "functionGroups",
    "externalReferences",
    "definedNames",
    "calcPr",
    "oleSize",
    "customWorkbookViews",
    "pivotCaches",
    "smartTagPr",
    "smartTagTypes",
    "webPublishing",
    "fileRecoveryPr",
    "webPublishObjects",
    "extLst"
  ]
                