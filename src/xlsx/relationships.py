from .xmlutils import XmlElement
from lxml.etree import _Element


class Relationships(XmlElement):

    def __init__(self, element: _Element):
        super().__init__(element or 
            XmlElement.new('Relationships', 
                nsmap = {None:'http://schemas.openxmlformats.org/package/2006/relationships'}))
        self._next_id = 1
        for child in self:
            id = int(child.attrib.get('Id')[3,])
            if id >= self._next_id:
                self._next_id = id + 1

    

        