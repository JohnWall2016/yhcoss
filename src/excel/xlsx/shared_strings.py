from typing import List, Optional, Union, Dict
from .xmlutils import XmlElement, XmlName, GenericElement


class RichText(XmlElement):
    def __init__(self, element: XmlElement):
        super().__init__(element)
        self._str = self._load_text()

    def _load_text(self) -> str:
        _str = ''
        for c in self:
            if c.tag.localname == 'r':
                for cc in c:
                    if cc.tag.localname == 't':
                        _str += cc.text or ''
        return _str

    def __str__(self):
        return self._str


class SharedStrings(XmlElement):
    namespace = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    xml_ns = 'http://www.w3.org/XML/1998/namespace'

    def __init__(self, element: Optional[XmlElement]):
        if element is None:
            element = XmlElement.new('sst',
                                  nsmap={ None: self.namespace })
        super().__init__(element)
        self._strlist: List[Union[str, RichText]] = []
        self._idxdict: Dict[Union[str, RichText], int] = {}
        self.remove_attrib('count', 'uniqueCount')
        self._cache_existing_shared_strings()

    def _cache_existing_shared_strings(self):
        index = 0
        for child in self:
            if child.tag.localname == 'si':
                content = child[0]
                if content.tag.localname == 't':
                    string = content.text or ''
                    self._strlist.append(string)
                    self._idxdict[string] = index
                    index += 1
                elif content.tag.localname == 'r':
                    r = RichText(child)
                    self._strlist.append(r)
                    self._idxdict[r] = index
                    index += 1
                else:
                    raise Exception(f'Unsupported element: {child}')

    def get_string_by_index(self, index: int) -> str:
        string = self._strlist[index]
        return f'{string}'

    def get_index_from_string(self, string: str) -> int:
        if string in self._idxdict:
            return self._idxdict[string]

        index = len(self._strlist)
        self._strlist.append(string)
        self._idxdict[string] = index

        elem = XmlElement.new('si')
        subelem = XmlElement.new('t')
        subelem.attrib[XmlName(self.xml_ns, 'space')] = 'preserve'
        subelem.text = string
        elem.append(subelem)
        self.append(elem)

        return index

                    
                            

