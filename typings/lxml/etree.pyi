# Hand-written stub for lxml.etree as used by mypy.report.
# This is *far* from complete, and the stubgen-generated ones crash mypy.
# Any use of `Any` below means I couldn't figure out the type.

from typing import (
    Any,
    Dict, Generic,
    IO,
    Iterable,
    Iterator,
    List,
    Mapping,
    Tuple,
    Union,
    Optional,
    Sequence,
    Sized,
    SupportsBytes,
    TypeVar,
    overload,
    # AnyStr
)

from typing_extensions import Protocol


# dummy for missing stubs
def __getattr__(name: str) -> Any: ...

# We do *not* want `typing.AnyStr` because it is a `TypeVar`, which is an
# unnecessary constraint. It seems reasonable to constrain each
# List/Dict argument to use one type consistently, though, and it is
# necessary in order to keep these brief.
_AnyStr = TypeVar('_AnyStr', str, bytes) #AnyStr
_AnySmartStr = Union['_ElementUnicodeResult', '_PyElementUnicodeResult', '_ElementStringResult']
# XPath object - http://lxml.de/xpathxslt.html#xpath-return-values
_XPathObject = Union[bool, float, _AnySmartStr, _AnyStr, List[Union['_Element', _AnySmartStr, _AnyStr, Tuple[Optional[_AnyStr], Optional[_AnyStr]]]]]
_ListAnyStr = List[_AnyStr]
_DictAnyStr = Dict[_AnyStr, _AnyStr]
_Dict_Tuple2AnyStr_Any = Dict[Tuple[_AnyStr], Any]
_NSMap = Dict[Optional[_AnyStr], _AnyStr]
_xpath = Union['XPath', _AnyStr]
_Namespace = Mapping[Optional[_AnyStr], Any]
_T = TypeVar('_T')

class ElementChildIterator(Generic[_AnyStr], Iterator['_Element[_AnyStr]']):
    def __iter__(self) -> 'ElementChildIterator[_AnyStr]': ...
    def __next__(self) -> '_Element[_AnyStr]': ...

class _ElementUnicodeResult(str):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[_AnyStr]
    def getparent(self) -> Optional['_Element']: ...

class _PyElementUnicodeResult(str):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[_AnyStr]
    def getparent(self) -> Optional['_Element']: ...

class _ElementStringResult(bytes):
    is_attribute: bool
    is_tail: bool
    is_text: bool
    attrname: Optional[_AnyStr]
    def getparent(self) -> Optional['_Element']: ...

class _Element(Generic[_AnyStr], Iterable['_Element'], Sized):
    def __delitem__(self, key: Union[int, slice]) -> None: ...
    def __getitem__(self, item: int) -> _Element[_AnyStr]: ...
    def __len__(self) -> int: ...
    def addprevious(self, element: '_Element[_AnyStr]') -> None: ...
    def addnext(self, element: '_Element[_AnyStr]') -> None: ...
    def append(self, element: '_Element[_AnyStr]') -> None: ...
    def cssselect(self, expression: str) -> List[_Element[_AnyStr]]: ...
    def find(self, path: _AnyStr, namespace: Optional[_Namespace] = ...) -> Optional['_Element[_AnyStr]']: ...
    def findall(self,
                name: str,
                namespace: Optional[_Namespace] = ...) -> List['_Element[_AnyStr]']: ...
    def clear(self) -> None: ...
    @overload
    def get(self, key: Union[_AnyStr, QName]) -> Optional[_AnyStr]: ...
    @overload
    def get(self, key: Union[_AnyStr, QName], default: _T) -> Union[_AnyStr, _T]: ...
    def getnext(self) -> Optional[_Element[_AnyStr]]: ...
    def getparent(self) -> Optional[_Element[_AnyStr]]: ...
    def getprevious(self) -> Optional[_Element[_AnyStr]]: ...
    def getroottree(self) -> _ElementTree: ...
    def insert(self, index: int, element: _Element[_AnyStr]) -> None: ...
    def iter(self,
             tag: Optional[_AnyStr] = ...,
             *tags: _AnyStr) -> Iterable[_Element]: ...
    def makeelement(self,
                    _tag: Union[_AnyStr, QName],
                    attrib: Optional[_DictAnyStr] = ...,
                    nsmap: Optional[_NSMap] = ...,
                    **_extra: Any
                    ) -> _Element[_AnyStr]: ...
    def remove(self, element: _Element[_AnyStr]) -> None: ...
    def xpath(self,
              _path: _AnyStr,
              namespaces: Optional[_DictAnyStr] = ...,
              extensions: Any = ...,
              smart_strings: bool = ...,
              **_variables: _XPathObject) -> _XPathObject: ...
    attrib: _Attrib[_AnyStr] = ...
    text: Optional[_AnyStr] = ...
    tag:  Union[_AnyStr, QName] = ...
    tail: Optional[_AnyStr] = ...
    nsmap: _NSMap = ...
    def __iter__(self) -> ElementChildIterator[_AnyStr]: ...
    def items(self) -> Sequence[Tuple[_AnyStr, _AnyStr]]: ...
    def iterfind(self, path: str, namespace: Optional[_Namespace] = None)  -> Iterator['_Element']: ...

class ElementBase(_Element): ...

class _ElementTree(Generic[_AnyStr]):
    parser = ... # type: XMLParser
    def getpath(self, element: _Element[_AnyStr]) -> str: ...
    def getroot(self) -> _Element[_AnyStr]: ...
    def write(self,
              file: Union[_AnyStr, IO[Any]],
              encoding: _AnyStr = ...,
              method: _AnyStr = ...,
              pretty_print: bool = ...,
              xml_declaration: Any = ...,
              with_tail: Any = ...,
              standalone: bool = ...,
              compression: int = ...,
              exclusive: bool = ...,
              with_comments: bool = ...,
              inclusive_ns_prefixes: _ListAnyStr = ...) -> None: ...
    def write_c14n(self,
                   file: Union[_AnyStr, IO[Any]],
                   with_comments: bool = ...,
                   compression: int = ...,
                   inclusive_ns_prefixes: Iterable[_AnyStr] = ...) -> None: ...
    def _setroot(self, root: _Element[_AnyStr]) -> None: ...
    def xpath(self,
              _path: _AnyStr,
              namespaces: Optional[_DictAnyStr] = ...,
              extensions: Any = ...,
              smart_strings: bool = ...,
              **_variables: _XPathObject) -> _XPathObject: ...
    def xslt(self,
             _xslt: XSLT,
             extensions: Optional[_Dict_Tuple2AnyStr_Any] = ...,
             access_control: Optional[XSLTAccessControl] = ...,
             **_variables: Any) -> _ElementTree: ...


class __ContentOnlyEleement(_Element): ...


class _Comment(__ContentOnlyEleement): ...


class _ProcessingInstruction(__ContentOnlyEleement):
    target: _AnyStr


class _Attrib(Generic[_AnyStr]):
    def __setitem__(self, key: Union[_AnyStr, QName], value: _AnyStr) -> None :...
    def __delitem__(self, key: Union[_AnyStr, QName]) -> None: ...
    def update(self,
               sequence_or_dict: Union[Sequence[Tuple[_AnyStr, _AnyStr]],
                                       Mapping[_AnyStr, _AnyStr]]) -> None: ...
    def pop(self, key: _AnyStr, default: _AnyStr) -> _AnyStr: ...
    def clear(self) -> None: ...
    def __repr__(self) -> str: ...
    def __copy__(self) -> _DictAnyStr: ...
    def __deepcopy__(self, memo: Dict[Any, Any]) -> _DictAnyStr: ...
    def __getitem__(self, key: Union[_AnyStr, QName]) -> _AnyStr: ...
    def __bool__(self) -> bool: ...
    def __len__(self) -> int: ...
    def get(self, key: _AnyStr, default: _AnyStr = ...) -> Optional[_AnyStr]: ...
    def keys(self) -> _ListAnyStr: ...
    def __iter__(self) -> Iterator[_AnyStr]: ...  # actually _AttribIterator
    def iterkeys(self) -> Iterator[_AnyStr]: ...
    def values(self) -> _ListAnyStr: ...
    def itervalues(self) -> Iterator[_AnyStr]: ...
    def items(self) -> List[Tuple[_AnyStr, _AnyStr]]: ...
    def iteritems(self) -> Iterator[Tuple[_AnyStr, _AnyStr]]: ...
    def has_key(self, key: Union[_AnyStr, QName]) -> bool: ...
    def __contains__(self, key: _AnyStr) -> bool: ...
    def __richcmp__(self, other: _Attrib, op: int) -> bool: ...


class QName:
    localname = ... # type: _AnyStr
    namespace = ... # type: _AnyStr
    text = ... # type: _AnyStr
    def __init__(self,
                 text_or_uri_element: Union[None, _AnyStr, _Element],
                 tag: Optional[_AnyStr] = ...) -> None: ...


class _XSLTResultTree(_ElementTree, SupportsBytes):
    def __bytes__(self) -> bytes: ...

class _XSLTQuotedStringParam: ...


# https://lxml.de/parsing.html#the-target-parser-interface
class ParserTarget(Protocol):
    def comment(self, text: _AnyStr) -> None: ...
    def close(self) -> Any: ...
    def data(self, data: _AnyStr) -> None: ...
    def end(self, tag: _AnyStr) -> None: ...
    def start(self, tag: _AnyStr, attrib: _DictAnyStr) -> None: ...

class XMLParser:
    def __init__(self,
                 encoding: Optional[_AnyStr] = ...,
                 attribute_defaults: bool = ...,
                 dtd_validation: bool = ...,
                 load_dtd: bool = ...,
                 no_network: bool = ...,
                 ns_clean: bool = ...,
                 recover: bool = ...,
                 schema: Optional[XMLSchema] = ...,
                 huge_tree: bool = ...,
                 remove_blank_text: bool = ...,
                 resolve_entities: bool = ...,
                 remove_comments: bool = ...,
                 remove_pis: bool = ...,
                 strip_cdata: bool = ...,
                 collect_ids: bool = ...,
                 target: Optional[ParserTarget] = ...,
                 compact: bool = ...) -> None: ...

class XMLSchema:
    def __init__(self,
                 etree: Union[_Element, _ElementTree] = ...,
                 file: Union[_AnyStr, IO[Any]] = ...) -> None: ...
    def assertValid(self, etree: Union[_Element, _ElementTree]) -> None: ...

class XSLTAccessControl: ...

class XSLT:
    def __init__(self,
                 xslt_input: Union[_Element, _ElementTree],
                 extensions: _Dict_Tuple2AnyStr_Any = ...,
                 regexp: bool = ...,
                 access_control: XSLTAccessControl = ...) -> None: ...
    def __call__(self,
                 _input: Union[_Element, _ElementTree],
                 profile_run: bool = ...,
                 **kwargs: Union[_AnyStr, _XSLTQuotedStringParam]) -> _XSLTResultTree: ...
    @staticmethod
    def strparam(s: _AnyStr) -> _XSLTQuotedStringParam: ...


def Comment(text: Optional[_AnyStr] = ...) -> _Comment: ...

def XML(text: _AnyStr) -> _Element[_AnyStr]: ...
def Element(_tag: _AnyStr,
            attrib: Optional[_DictAnyStr] = ...,
            nsmap: Optional[_NSMap] = ...,
            **extra: _AnyStr) -> _Element[_AnyStr]: ...
def SubElement(_parent: _Element, _tag: _AnyStr,
               attrib: Optional[_DictAnyStr] = ...,
               nsmap: Optional[_NSMap] = ...,
               **extra: _AnyStr) -> _Element: ...
def ElementTree(element: _Element[_AnyStr] = ...,
                file: Union[_AnyStr, IO[Any]] = ...,
                parser: XMLParser = ...) -> _ElementTree[_AnyStr]: ...
def ProcessingInstruction(
        target: _AnyStr,
        text: _AnyStr = ...
) -> _ProcessingInstruction: ...

PI = ProcessingInstruction

def cleanup_namespaces(tree_or_element: Union[_Element, _ElementTree],
                       top_nsmap: Optional[_NSMap] = ...,
                       keep_ns_prefixes: Optional[Iterable[_AnyStr]] = ...) -> None: ...

def parse(source: Union[_AnyStr, IO[Any]],
          parser: XMLParser = ...,
          base_url: _AnyStr = ...) -> _ElementTree: ...
def fromstring(text: _AnyStr,
               parser: XMLParser = ...,
               *,
               base_url: _AnyStr = ...) -> _Element: ...
def tostring(element_or_tree: Union[_Element[_AnyStr], _ElementTree[_AnyStr]],
             encoding: Union[str, type] = ...,
             method: str = ...,
             xml_declaration: bool = ...,
             pretty_print: bool = ...,
             with_tail: bool = ...,
             standalone: bool = ...,
             doctype: str = ...,
             exclusive: bool = ...,
             with_comments: bool = ...,
             inclusive_ns_prefixes: Any = ...) -> _AnyStr: ...

class _ErrorLog: ...

class Error(Exception): ...

class LxmlError(Error):
    def __init__(self, message: Any, error_log: _ErrorLog = ...) -> None: ...
    error_log = ...  # type: _ErrorLog

class DocumentInvalid(LxmlError): ...
class LxmlSyntaxError(LxmlError, SyntaxError): ...
class ParseError(LxmlSyntaxError): ...
class XMLSyntaxError(ParseError): ...

class _Validator: ...

class DTD(_Validator):
    def __init__(self,
                 file: Union[_AnyStr, IO[Any]] = ...,
                 *,
                 external_id: Any = ...) -> None: ...

    def assertValid(self, etree: _Element) -> None: ...

class XPath:
    def __init__(self,
                 path: _AnyStr,
                 *,
                 namespaces: Optional[_AnyStr] = ...,
                 extensions: Optional[_AnyStr] = ...,
                 regexp: bool = ...,
                 smart_strings: bool = ...) -> None: ...
    def __call__(self, _etree_or_element: Union[_Element, _ElementTree], **_variables: _XPathObject) -> _XPathObject: ...
