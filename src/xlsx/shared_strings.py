from typing import Optional
from .xmlutils import XmlElement
from lxml.etree import _Element


class Relationships(XmlElement):
    namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

    def __init__(self, element: _Element):
        super().__init__(element or
                         XmlElement.new('sst',
                                        nsmap={None: self.namespace}))
        
