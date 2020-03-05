from .xmlutils import XmlElement, GenericElement


class AppProperties(XmlElement):
    def __init__(self, element: GenericElement[str]):
        super().__init__(element)