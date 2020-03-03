from typing import Callable, Collection, Iterator, Optional, cast, Union, Dict, Mapping, Any, TypeVar
from lxml.etree import _Element, tostring, Element
from lxml.etree import _Attrib as XmlAttribute, QName as XmlName

AnyStr = Union[str, bytes]
NSMap = Dict[Union[str, None], str]
DictAnyStr = Union[Dict[str, str], Dict[bytes, bytes]]
OptionalNamespace = Optional[Mapping[Optional[str], Any]]


class XmlElement:
    def __init__(self, element: Union[_Element, 'XmlElement']):
        if isinstance(element, XmlElement):
            self._element = element._element
        else:
            self._element = element

    @staticmethod
    def new(tag: str, attrib: Optional[DictAnyStr] = None, 
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

    def find(self, name_or_path: str, namespace: OptionalNamespace = None) -> Optional['XmlElement']:
        elem = self._element.find(name_or_path, namespace)
        if elem is not None:
            return XmlElement(elem)
        return None

    def find_by_localname(self, localname: str) -> Optional['XmlElement']:
        return self.find(localname, self.nsmap)

    def find_by_attrib(self, attr_name: Union[AnyStr, XmlName], attr_value: AnyStr) -> Optional['XmlElement']:
        for child in self:
            if child.get_attrib_value(attr_name) == attr_value:
                return child
        return None

    def get_attrib_value(self, attr_name: Union[AnyStr, XmlName], default: Optional[AnyStr] = None) -> Optional[AnyStr]:
        return self._element.get(attr_name, default)

    def remove(self, index_or_localname_or_elem: Union[int, str, 'XmlElement']):
        if isinstance(index_or_localname_or_elem, int):
            del self._element[index_or_localname_or_elem]
        elif isinstance(index_or_localname_or_elem, str):
            elem = self.find_by_localname(index_or_localname_or_elem)
            if elem:
                self.remove(elem)
        else:
            self._element.remove(index_or_localname_or_elem._element)

    def remove_if(self, cond: Callable[['XmlElement'], bool]):
        elems = []
        for child in self:
            if cond(child):
                elems.append(child)
        for elem in elems:
            self.remove(elem)

    def remove_if_empty(self, localname: str):
        self.remove_if(
            lambda e:
                e.tag.localname == localname and
                len(e) == 0 and
                len(e.attrib) == 0)

    def remove_attrib(self, *attr_names: Union[AnyStr, XmlName]):
        for name in attr_names or []:
            if self.attrib.has_key(name):
                del self.attrib[name]

    def clear(self):
        self._element.clear()

    def put_attrib(self, attrs: Dict[Union[AnyStr, XmlName], Optional[AnyStr]]):
        for k, v in attrs.items():
            if k in self.attrib and v is None:
                del self.attrib[k]
            elif v:
                self.attrib[k] = v

    def put_child_attrib(self, localname: str, attrs: Dict[Union[AnyStr, XmlName], Optional[AnyStr]]):
        child = self.append_if_not_found(localname)
        child.put_attrib(attrs)

    def insert(self, index: int, element: 'XmlElement'):
        self._element.insert(index, element._element)
        
    def append(self, element: 'XmlElement'):
        self._element.append(element._element)

    def get_child_attrib_value(self, localname: str, attr: str) -> Optional[AnyStr]:
        c = self.find_by_localname(localname)
        if c:
            return c.attrib.get(attr)
        return None

    def append_if_not_found(self, localname: str) -> 'XmlElement':
        elem = self.find_by_localname(localname)
        if elem:
            return elem
        elem = XmlElement.new(localname)
        self.append(elem)
        return elem

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


NoneElement = XmlElement.new('__NONE__')


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def try_parse_default(type_: Callable[[T], U], value: T, default: V):
    try:
        return type_(value)
    except:
        return default

def try_parse(type_: Callable[[T], U], value: T):
    return try_parse_default(type_, value, None)

def to_str(anystr: Union[AnyStr, int], encoding: str = 'utf-8') -> str:
    if isinstance(anystr, str):
        return anystr
    elif isinstance(anystr, int):
        return str(anystr)
    return str(anystr, encoding)

def to_optstr(anystr: Optional[Union[AnyStr, int]], encoding: str = 'utf-8') -> Optional[str]:
    if anystr is None or isinstance(anystr, str):
        return anystr
    elif isinstance(anystr, int):
        return str(anystr)
    return str(anystr, encoding)
