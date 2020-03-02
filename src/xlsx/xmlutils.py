from typing import Iterator, Optional, cast, Union, Dict, Mapping, Any, TypeVar
from lxml.etree import _Element, tostring, Element
from lxml.etree import _Attrib as XmlAttribute, QName as XmlName


NSMap = Dict[Union[str, None], str]
DictStr = Dict[str, str]
OptionalNamespace = Optional[Mapping[Optional[str], Any]]
AnyStr = Union[str, bytes]

T = TypeVar('T')

class XmlElement:
    def __init__(self, element: Union[_Element, 'XmlElement']):
        if isinstance(element, XmlElement):
            self._element = element._element
        else:
            self._element = element

    @staticmethod
    def new(tag: str, attrib: Optional[DictStr] = None, 
            nsmap: Optional[NSMap] = None) -> 'XmlElement':
        return XmlElement(Element(tag, attrib=attrib, nsmap=nsmap))

    @property
    def attrib(self) -> XmlAttribute:
        return self._element.attrib

    @property
    def nsmap(self) -> NSMap:
        return cast(NSMap, self._element.nsmap)

    @property
    def tag(self) -> XmlName:
        tag = self._element.tag
        return tag if isinstance(tag, XmlName) else XmlName(tag)

    @property
    def text(self):
        return self._element.text

    @text.setter
    def text(self, value: Optional[AnyStr]):
        self._element.text = value

    def find(self, child_path: str, namespace: OptionalNamespace = None) -> Optional['XmlElement']:
        elem = self._element.find(child_path, namespace)
        if elem is not None:
            return XmlElement(elem)
        return None

    def find_by_attr(self, name: Union[AnyStr, XmlName], value: AnyStr) -> Optional['XmlElement']:
        for child in self:
            if child.get(name) == value:
                return child
        return None

    def get(self, attr_name: Union[AnyStr, XmlName], default: Optional[AnyStr] = None) -> Optional[AnyStr]:
        return self._element.get(attr_name, default)

    def remove(self, index_or_elem: Union[int, 'XmlElement']):
        if isinstance(index_or_elem, int):
            del self._element[index_or_elem]
        else:
            self._element.remove(index_or_elem._element)

    def remove_attrib(self, *attr_names: Union[AnyStr, XmlName]):
        for name in attr_names or []:
            if self.attrib.has_key(name):
                del self.attrib[name]

    def insert(self, index: int, element: 'XmlElement'):
        self._element.insert(index, element._element)
        
    def append(self, element: 'XmlElement'):
        self._element.append(element._element)

    def tostring(self, **kwargs):
        return tostring(self._element, **kwargs)

    def __iter__(self) -> Iterator['XmlElement']:
        for e in self._element:
            yield XmlElement(e)

    def __len__(self) -> int:
        return len(self._element)

    def __getitem__(self, index: int) -> 'XmlElement':
        return XmlElement(self._element[index])

    def __repr__(self) -> str:
        return cast(str, tostring(self._element, encoding='unicode', pretty_print=True))

    def __str__(self) -> str:
        return cast(str, tostring(self._element, encoding='unicode', pretty_print=False))

