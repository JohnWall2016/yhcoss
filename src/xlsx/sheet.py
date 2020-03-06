from os import name
from .relationships import Relationships
from .workbook import *
from .xmlutils import XmlElement

class Sheet(XmlElement):
    namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

    def __init__(self, workbook: 'Workbook', id: XmlElement, element: XmlElement, relationships: XmlElement):
        super().__init__(element or (
            XmlElement.new('worksheet',
                           nsmap = {
                               None: self.namespace,
                               'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
                               'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
                               'mc:Ignorable': 'x14ac',
                               'x14ac': 'http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac'
                           })
        ))
        self._workbook = workbook
        self._id = id
        self._relationships = Relationships(relationships)
        self.append(XmlElement.new('sheetData'))
        self._max_shared_formula_id = -1
        self.remove('dimension')
        self._sheet_data = self.find_by_localname('sheetData')
        if self._sheet_data is not None:
            self.remove(self._sheet_data)
        # TODO

    @property
    def workbook(self) -> 'Workbook':
        return self._workbook

    @property
    def name(self):
        return self.get_attrib_value('name')

    @name.setter
    def name(self, value: str):
        self.attrib['name'] = value

    def update_max_shared_formula_id(self, shared_formula_id: int):
        if shared_formula_id > self._max_shared_formula_id:
            self._max_shared_formula_id = shared_formula_id

