from typing import Optional, Union
from .style_sheet import StyleSheet
from .xmlutils import XmlElement, AnyStr, try_parse, to_str


class Color:

    def __init__(self, rgb: AnyStr = None, theme: int = None, tint: AnyStr = None):
        self.rgb: Optional[AnyStr] = rgb
        self.theme: Optional[int] = theme
        self.tint: Optional[AnyStr] = tint

    @property
    def empty(self):
        return self.rgb or self.theme or self.tint

    @staticmethod
    def new(elem: XmlElement) -> Optional['Color']:
        color = Color()
        color.rgb = elem.get_attrib_value('rgb')
        color.theme = try_parse(int, elem.get_attrib_value('theme'))
        if color.rgb is None:
            index = try_parse(int, elem.get_attrib_value('indexed'))
            if index:
                color.rgb = colors[index]
        color.tint = elem.get_attrib_value('tint')
        return None if color.empty else color


class Style:

    def __init__(self, sheet: StyleSheet, id: int, xf: XmlElement, font: XmlElement, fill: XmlElement, border: XmlElement):
        self._sheet = sheet
        self._id = id
        self._xf = xf
        self._font = font
        self._fill = fill
        self._border = border

    @property
    def id(self):
        return self._id

    def _get_color(self, elem: XmlElement, localname: str) -> Optional[Color]:
        child = elem.find_by_localname(localname)
        if child:
            return Color.new(child)
        return None

    def _set_color(self, elem: XmlElement, localname: str, color: Optional[Union[str, int, Color]]):
        clr = None
        if isinstance(color, str):
            clr = Color(rgb=color)
        elif isinstance(color, int):
            clr = Color(theme=color)
        else:
            clr = color

        if clr is None or clr.empty:
            elem.remove(localname)
        else:
            def to_upper(str: Optional[AnyStr]) -> Optional[str]:
                return to_str(str).upper() if str else None
            elem.put_child_attrib(localname,
                                  {
                                      'rgb': to_upper(clr.rgb),
                                      'indexed': None,
                                      'theme': to_str(clr.theme),
                                      'tint': clr.tint
                                  })
            elem.remove_if_empty(localname)

    @property
    def bold(self) -> bool:
        return self._font.find_by_localname('b') != None

    @bold.setter
    def bold(self, value: bool):
        if value:
            self._font.append_if_not_found('b')
        else:
            self._font.remove('b')

    @property
    def underline(self) -> bool:
        return self._font.find_by_localname('u') != None

    @underline.setter
    def underline(self, value: Union[bool, str]):
        if isinstance(value, bool):
            if value:
                self._font.append_if_not_found('u')
            else:
                self._font.remove('u')
        else:
            self._font.append_if_not_found('u').attrib['val'] = value


colors = [
    "000000",
    "FFFFFF",
    "FF0000",
    "00FF00",
    "0000FF",
    "FFFF00",
    "FF00FF",
    "00FFFF",
    "000000",
    "FFFFFF",
    "FF0000",
    "00FF00",
    "0000FF",
    "FFFF00",
    "FF00FF",
    "00FFFF",
    "800000",
    "008000",
    "000080",
    "808000",
    "800080",
    "008080",
    "C0C0C0",
    "808080",
    "9999FF",
    "993366",
    "FFFFCC",
    "CCFFFF",
    "660066",
    "FF8080",
    "0066CC",
    "CCCCFF",
    "000080",
    "FF00FF",
    "FFFF00",
    "00FFFF",
    "800080",
    "800000",
    "008080",
    "0000FF",
    "00CCFF",
    "CCFFFF",
    "CCFFCC",
    "FFFF99",
    "99CCFF",
    "FF99CC",
    "CC99FF",
    "FFCC99",
    "3366FF",
    "33CCCC",
    "99CC00",
    "FFCC00",
    "FF9900",
    "FF6600",
    "666699",
    "969696",
    "003366",
    "339966",
    "003300",
    "333300",
    "993300",
    "993366",
    "333399",
    "333333",
    "System Foreground",
    "System Background"
]
