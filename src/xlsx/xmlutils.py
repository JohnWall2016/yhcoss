from typing import Iterator, Optional, cast, Union, Dict, Mapping, Any
from lxml.etree import _Element, tostring
from lxml.etree import _Attrib as XmlAttribute, QName as XmlName

NSMap = Dict[Union[str, None], str]
OptionalNamespace = Optional[Mapping[Optional[str], Any]]
AnyStr = Union[str, bytes]

class XmlElement:
    def __init__(self, element: _Element):
        self._element = element

    @property
    def attrib(self) -> XmlAttribute:
        return self._element.attrib

    @property
    def nsmap(self) -> NSMap:
        return cast(NSMap, self._element.nsmap)

    @property
    def tag(self):
        return self._element.tag

    def find(self, child_path: str, namespace: OptionalNamespace = None) -> Optional['XmlElement']:
        elem = self._element.find(child_path, namespace)
        if elem is not None:
            return XmlElement(elem)
        return None

    def get(self, attr_name: AnyStr, namespace: OptionalNamespace = None) -> Optional[AnyStr]:
        value = self._element.get(attr_name)
        if value:
            return value
        if namespace:
            for ns in namespace.values():
                value = self._element.get(XmlName(ns, attr_name).text)
                if value:
                    return value
        return None


    def remove(self, index_or_elem: Union[int, 'XmlElement']):
        if isinstance(index_or_elem, int):
            del self._element[index_or_elem]
        else:
            self._element.remove(index_or_elem._element)

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
