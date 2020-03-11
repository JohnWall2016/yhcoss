from .xmlutils import XmlElement, GenericElement


class AppProperties(XmlElement):
    def __init__(self, element: XmlElement):
        super().__init__(element)