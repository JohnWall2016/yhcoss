from typing import Optional
from .xmlutils import XmlElement, _Element

class ContentTypes(XmlElement):
    def __init__(self, element: _Element):
        super().__init__(element)

    def add(self, part_name: str, content_type: str) -> XmlElement:
        return XmlElement.new('Override',
                              {
                                  'PartName': part_name,
                                  'ContentType': content_type
                              })

    def find_by_part_name(self, part_name: str) -> Optional[XmlElement]:
        return self.find_by_attrib('PartName', part_name)


    