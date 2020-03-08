from typing import Any, Union, Optional

from lxml.etree import ElementBase, XMLParser, _Attrib, _Element


# dummy for missing stubs
def __getattr__(name) -> Any: ...


class ObjectifiedElement(ElementBase):
    pass

def fromstring(text: Union[bytes, str],
               parser: XMLParser = ...,
               *,
               base_url: Union[bytes, str] = ...) -> ObjectifiedElement: ...

def Element(_tag: str, attrib=None, nsmap=None, _pytype=None, **_attributes) -> _Element: ...
