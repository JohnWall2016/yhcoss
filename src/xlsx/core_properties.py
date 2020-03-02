from .xmlutils import XmlElement
from lxml.etree import _Element


class CoreProperties(XmlElement):
    def __init__(self, element: _Element):
        super().__init__(element)