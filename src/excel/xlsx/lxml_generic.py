from typing import (Generic, Iterable, Iterator, Sized, Union, List, Dict, Mapping,
                    Optional, overload, AnyStr, Any, Tuple, Sequence, TypeVar, IO,
                    cast)
from lxml.etree import (XPath, XMLParser, XSLT, XSLTAccessControl, QName, 
                        Element as _Element, XML as _XML, tostring as _tostring,
                        ElementTree as _ElementTree)


AnySmartStr = Union['ElementUnicodeResult', 'PyElementUnicodeResult', 'ElementStringResult']
XPathObject = Union[bool, float, AnySmartStr, AnyStr, 
                    List[Union['GenericElement', AnySmartStr, AnyStr, Tuple[Optional[AnyStr], 
                                Optional[AnyStr]]]]]
ListAnyStr = List[AnyStr]
DictAnyStr = Dict[AnyStr, AnyStr]
Dict_Tuple2AnyStr_Any = Dict[Tuple[AnyStr], Any]
NSMap = Dict[Optional[AnyStr], AnyStr]
xpath = Union['XPath', AnyStr]
Namespace = Mapping[Optional[AnyStr], Any]
T = TypeVar('T')


class ElementUnicodeResult(str):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[AnyStr]
    def getparent(self) -> Optional['GenericElement']: ...


class PyElementUnicodeResult(str):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[AnyStr]
    def getparent(self) -> Optional['GenericElement']: ...


class ElementStringResult(bytes):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[AnyStr]
    def getparent(self) -> Optional['GenericElement']: ...


class GenericQName(QName, Generic[AnyStr]):
    def __init__(self,
                 text_or_uri_element: Union[None, AnyStr, 'GenericElement[AnyStr]'],
                 tag: Optional[AnyStr] = None):
        super().__init__(cast(Any, text_or_uri_element), tag)

    @property
    def localname(self) -> AnyStr:
        return super().localname

    @property
    def namespace(self) -> Optional[AnyStr]:
        return super().namespace

    @property
    def text(self) -> AnyStr:
        return super().text

    def __str__(self) -> str:
        return f'{self.text}'

    def __repr__(self) -> str:
        return f'{self.text}'


class GenericElement(Generic[AnyStr], Iterable['GenericElement'], Sized):
    def __delitem__(self, key: Union[int, slice]) -> None: ...
    def __getitem__(self, item: int) -> 'GenericElement[AnyStr]': ...
    def __len__(self) -> int: ...
    def addprevious(self, element: 'GenericElement[AnyStr]') -> None: ...
    def addnext(self, element: 'GenericElement[AnyStr]') -> None: ...
    def append(self, element: 'GenericElement[AnyStr]') -> None: ...
    def cssselect(self, expression: str) -> List['GenericElement[AnyStr]']: ...
    def find(self, path: AnyStr, namespace: Optional[Namespace] = ...) -> Optional['GenericElement[AnyStr]']: ...
    def findall(self,
                name: str,
                namespace: Optional[Namespace] = ...) -> List['GenericElement[AnyStr]']: ...
    def clear(self) -> None: ...
    @overload
    def get(self, key: Union[AnyStr, GenericQName[AnyStr]]) -> Optional[AnyStr]: ...
    @overload
    def get(self, key: Union[AnyStr, GenericQName[AnyStr]], default: T) -> Union[AnyStr, T]: ...
    def getnext(self) -> Optional['GenericElement[AnyStr]']: ...
    def getparent(self) -> Optional['GenericElement[AnyStr]']: ...
    def getprevious(self) -> Optional['GenericElement[AnyStr]']: ...
    def getroottree(self) -> 'GenericElementTree[AnyStr]': ...
    def insert(self, index: int, element: 'GenericElement[AnyStr]') -> None: ...
    def iter(self,
             tag: Optional[AnyStr] = ...,
             *tags: AnyStr) -> Iterable['GenericElement[AnyStr]']: ...
    def makeelement(self,
                    _tag: Union[AnyStr, GenericQName[AnyStr]],
                    attrib: Optional[DictAnyStr] = ...,
                    nsmap: Optional[NSMap] = ...,
                    **_extra: Any
                    ) -> 'GenericElement[AnyStr]': ...
    def remove(self, element: 'GenericElement[AnyStr]') -> None: ...
    def xpath(self,
              _path: AnyStr,
              namespaces: Optional[DictAnyStr] = ...,
              extensions: Any = ...,
              smart_strings: bool = ...,
              **_variables: XPathObject) -> XPathObject: ...
    @property
    def attrib(self) -> 'GenericAttrib[AnyStr]': ...
    text: Optional[AnyStr] = ...
    tag:  Union[AnyStr, GenericQName[AnyStr]] = ...
    tail: Optional[AnyStr] = ...
    @property
    def nsmap(self) -> NSMap: ...
    def __iter__(self) -> 'GenericElementChildIterator[AnyStr]': ...
    def items(self) -> Sequence[Tuple[AnyStr, AnyStr]]: ...
    def iterfind(self, path: str, namespace: Optional[Namespace] = None)  -> Iterator['GenericElement[AnyStr]']: ...

class GenericElementChildIterator(Generic[AnyStr], Iterator['GenericElement[AnyStr]']):
    def __iter__(self) -> 'GenericElementChildIterator[AnyStr]': ...
    def __next__(self) -> 'GenericElement[AnyStr]': ...

class GenericAttrib(Generic[AnyStr]):
    def __setitem__(self, key: Union[AnyStr, GenericQName[AnyStr]], value: AnyStr) -> None :...
    def __delitem__(self, key: Union[AnyStr, GenericQName[AnyStr]]) -> None: ...
    def update(self,
               sequence_or_dict: Union[Sequence[Tuple[AnyStr, AnyStr]],
                                       Mapping[AnyStr, AnyStr]]) -> None: ...
    def pop(self, key: AnyStr, default: AnyStr) -> AnyStr: ...
    def clear(self) -> None: ...
    def __repr__(self) -> str: ...
    def __copy__(self) -> DictAnyStr: ...
    def __deepcopy__(self, memo: Dict[Any, Any]) -> DictAnyStr: ...
    def __getitem__(self, key: Union[AnyStr, GenericQName[AnyStr]]) -> AnyStr: ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int: ...
    def get(self, key: AnyStr, default: AnyStr = ...) -> Optional[AnyStr]: ...
    def keys(self) -> ListAnyStr: ...
    def __iter__(self) -> Iterator[AnyStr]: ...  # actually _AttribIterator
    def iterkeys(self) -> Iterator[AnyStr]: ...
    def values(self) -> ListAnyStr: ...
    def itervalues(self) -> Iterator[AnyStr]: ...
    def items(self) -> List[Tuple[AnyStr, AnyStr]]: ...
    def iteritems(self) -> Iterator[Tuple[AnyStr, AnyStr]]: ...
    def has_key(self, key: Union[AnyStr, GenericQName[AnyStr]]) -> bool: ...
    def __contains__(self, key: AnyStr) -> bool: ...
    def __richcmp__(self, other: 'GenericAttrib[AnyStr]', op: int) -> bool: ...


class GenericElementTree(Generic[AnyStr]):
    @property
    def parse(self) -> XMLParser: ...
    def getpath(self, element: GenericElement[AnyStr]) -> str: ...
    def getroot(self) -> GenericElement[AnyStr]: ...
    def write(self,
              file: Union[AnyStr, IO[Any]],
              encoding: AnyStr = ...,
              method: AnyStr = ...,
              pretty_print: bool = ...,
              xml_declaration: Any = ...,
              with_tail: Any = ...,
              standalone: bool = ...,
              compression: int = ...,
              exclusive: bool = ...,
              with_comments: bool = ...,
              inclusive_ns_prefixes: ListAnyStr = ...) -> None: ...
    def write_c14n(self,
                   file: Union[AnyStr, IO[Any]],
                   with_comments: bool = ...,
                   compression: int = ...,
                   inclusive_ns_prefixes: Iterable[AnyStr] = ...) -> None: ...
    def _setroot(self, root: GenericElement[AnyStr]) -> None: ...
    def xpath(self,
              _path: AnyStr,
              namespaces: Optional[DictAnyStr] = ...,
              extensions: Any = ...,
              smart_strings: bool = ...,
              **_variables: XPathObject) -> XPathObject: ...
    def xslt(self,
             _xslt: XSLT,
             extensions: Optional[Dict_Tuple2AnyStr_Any] = ...,
             access_control: Optional[XSLTAccessControl] = ...,
             **_variables: Any) -> 'GenericElementTree[AnyStr]': ...


def XML(text: Union[str, bytes]) -> GenericElement:
    return cast(Any, _XML(text))

_NSMap = Union[Dict[Optional[str], str], Dict[Optional[bytes], bytes]]

def Element(_tag: AnyStr,
            attrib: Optional[DictAnyStr] = None,
            nsmap: Optional[_NSMap] = None,
            **extra: AnyStr) -> GenericElement[AnyStr]:
    return cast(Any, _Element(_tag, attrib, nsmap, **extra))

def tostring(element_or_tree: Union[GenericElement[AnyStr], GenericElementTree[AnyStr]],
             *,
             encoding: Union[str, type] = None,
             method: str = 'xml',
             xml_declaration: bool = None,
             pretty_print: bool = False,
             with_tail: bool = True,
             standalone: bool = None,
             doctype: str = None,
             exclusive: bool = False,
             inclusive_ns_prefixes: Any = None,
             with_comments: bool = True,
             strip_text: bool = False) -> AnyStr:
    return _tostring(cast(Any, element_or_tree), 
                     encoding=encoding, 
                     method=method,
                     xml_declaration=xml_declaration,
                     pretty_print=pretty_print, 
                     with_tail=with_tail, 
                     standalone=standalone,
                     doctype=doctype,
                     exclusive=exclusive,
                     inclusive_ns_prefixes=inclusive_ns_prefixes,
                     with_comments=with_comments,
                     strip_text=strip_text)

def ElementTree(element: GenericElement[AnyStr] = None,
                *,
                file: Union[AnyStr, IO[Any]] = None,
                parser: XMLParser = None) -> GenericElementTree[AnyStr]:
    return cast(Any, _ElementTree(cast(Any, element), file=file, parser=parser))

