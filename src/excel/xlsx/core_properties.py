from .xmlutils import XmlElement, GenericElement


class CoreProperties(XmlElement):
    def __init__(self, element: XmlElement):
        super().__init__(element)