from typing import Optional, Union
from .xmlutils import XmlElement, try_parse_default, GenericElement


class Relationships(XmlElement):
    relationshipSchemaPrefix = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"

    def __init__(self, element: Optional[XmlElement]):
        if element is None:
            element = XmlElement.new('Relationships',
                                    nsmap={None: 'http://schemas.openxmlformats.org/package/2006/relationships'})
        super().__init__(element)
        self._next_id = 1
        for child in self:
            id = try_parse_default(int, child.attrib.get('Id')[3:], None)
            if id and id >= self._next_id:
                self._next_id = id + 1

    def add(self, type_: str, target: str, target_mode: Optional[str] = None) -> XmlElement:
        elem = XmlElement.new('Relationship',
                              {
                                  'Id': f'rId{self._next_id}',
                                  'Type': f'{self.relationshipSchemaPrefix}{type_}',
                                  'Target': target
                              })
        if target_mode:
            elem.attrib['TargetMode'] = target_mode
        self._next_id += 1
        return elem

    def find_by_id(self, id: str):
        return self.find_by_attrib('Id', id)

    def find_by_type(self, type_: str):
        return self.find_by_attrib('Type', f'{self.relationshipSchemaPrefix}{type_}')
