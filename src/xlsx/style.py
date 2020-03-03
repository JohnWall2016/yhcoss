from typing import Optional, Union, List
from .style_sheet import StyleSheet
from .xmlutils import XmlElement, AnyStr, try_parse, to_str, to_optstr


class Color:

    def __init__(self, rgb: AnyStr = None, theme: int = None,
                 tint: AnyStr = None):
        self.rgb: Optional[AnyStr] = rgb
        self.theme: Optional[int] = theme
        self.tint: Optional[AnyStr] = tint

    @property
    def empty(self):
        return not (self.rgb or self.theme or self.tint)

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


class Stop:
    def __init__(self, position: AnyStr, color: Color = None):
        self.position = to_str(position)
        self.color = color


class Fill:
    pass


class SolidFile(Fill):
    def __init__(self, color: Color = None):
        self.color = color


class PatternFill(Fill):
    def __init__(self, type_: AnyStr, foreground: Color = None,
                 background: Color = None):
        self.type = to_str(type_)
        self.foreground = foreground
        self.background = background


class GradientFill(Fill):
    def __init__(self, type_: AnyStr, stops: List[Stop] = None,
                 angle: AnyStr = None, left: AnyStr = None, right: AnyStr = None,
                 top: AnyStr = None, bottom: AnyStr = None):
        self.type = type_
        self.stops = stops
        self.angle = angle
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


class Side:
    def __init__(self, style: Optional[str] = None,
                 color: Optional[Color] = None, direction: Optional[str] = None):
        self.style = style
        self.color = color
        self.direction = direction
        
    @property
    def empty(self) -> bool:
        return not (self.style or self.color or self.direction)


class Border:
    def __init__(self, left: Side = None, right: Side = None,
                 top: Side = None, bottem: Side = None,
                 diagonal: Side = None):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottem
        self.diagonal = diagonal


class Style:

    def __init__(self, sheet: StyleSheet, id: int, xf: XmlElement,
                 font: XmlElement, fill: XmlElement, border: XmlElement):
        self._sheet = sheet
        self._id = id
        self._xf = xf
        self._font = font
        self._fill = fill
        self._border = border

    @property
    def id(self):
        return self._id

    def _get_color(self, elem: Optional[XmlElement], localname: str) -> Optional[Color]:
        if elem is None:
            return None
        child = elem.find_by_localname(localname)
        if child:
            return Color.new(child)
        return None

    def _set_color(self, elem: XmlElement, localname: str,
                   color: Optional[Union[str, int, Color]]):
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
                                      'theme': to_optstr(clr.theme),
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

    @property
    def strike(self) -> bool:
        return self._font.find_by_localname('strike') != None

    @strike.setter
    def strike(self, value: bool):
        if value:
            self._font.append_if_not_found('strike')
        else:
            self._font.remove('strike')

    def _get_font_vertical_alignment(self):
        return self._font.get_child_attrib_value('vertAlign', 'val')

    def _set_font_vertical_alignment(self, value: Optional[str]):
        self._font.put_child_attrib('vertAlign', {'val':value})
        self._font.remove_if_empty('vertAlign')

    @property
    def subscript(self) -> bool:
        return self._get_font_vertical_alignment() == 'subscript'

    @subscript.setter
    def subscript(self, value: bool):
        self._set_font_vertical_alignment('subscript' if value else None)

    @property
    def superscript(self) -> bool:
        return self._get_font_vertical_alignment() == 'superscript'

    @superscript.setter
    def superscript(self, value: bool):
        self._set_font_vertical_alignment('superscript' if value else None)
    
    @property
    def font_size(self) -> Optional[int]:
        return try_parse(int, self._font.get_child_attrib_value('sz', 'val'))

    @font_size.setter
    def font_size(self, value: Optional[int]):
        self._font.put_child_attrib('sz', {'val': to_optstr(value)})
        self._font.remove_if_empty('sz')

    @property
    def font_family(self) -> Optional[AnyStr]:
        return self._font.get_child_attrib_value('name', 'val')

    @font_family.setter
    def font_family(self, value: Optional[AnyStr]):
        self._font.put_child_attrib('name', {'val': value})
        self._font.remove_if_empty('name')

    @property
    def font_color(self) -> Optional[Color]:
        return self._get_color(self._font, 'color')

    @font_color.setter
    def font_color(self, value: Optional[Union[str, int, Color]]):
        self._set_color(self._font, 'color', value)

    @property
    def horizontal_alignment(self) -> Optional[AnyStr]:
        return self._xf.get_child_attrib_value('alignment', 'horizontal')

    @horizontal_alignment.setter
    def horizontal_alignment(self, value: Optional[str]):
        self._xf.put_child_attrib('alignment', {'horizontal':value})
        self._xf.remove_if_empty('alignment')

    @property
    def vertical_alignment(self) -> Optional[AnyStr]:
        return self._xf.get_child_attrib_value('alignment', 'vertical')

    @vertical_alignment.setter
    def vertical_alignment(self, value: Optional[str]):
        self._xf.put_child_attrib('alignment', {'vertical':value})
        self._xf.remove_if_empty('alignment')


    @property
    def indent(self) -> Optional[AnyStr]:
        return self._xf.get_child_attrib_value('alignment', 'indent')

    @indent.setter
    def indent(self, value: Optional[str]):
        self._xf.put_child_attrib('alignment', {'indent':value})
        self._xf.remove_if_empty('alignment')

    @property
    def justify_lastline(self) -> bool:
        return self._xf.get_child_attrib_value('alignment', 'justifyLastLine') == '1'

    @justify_lastline.setter
    def justify_lastline(self, value: bool):
        self._xf.put_child_attrib('alignment', {'justifyLastLine': '1' if value else None})
        self._xf.remove_if_empty('alignment')

    @property
    def wrap_text(self) -> bool:
        return self._xf.get_child_attrib_value('alignment', 'wrapText') == '1'

    @wrap_text.setter
    def wrap_text(self, value: bool):
        self._xf.put_child_attrib('alignment', {'wrapText': '1' if value else None})
        self._xf.remove_if_empty('alignment')

    @property
    def shrink_to_fit(self) -> bool:
        return self._xf.get_child_attrib_value('alignment', 'shrinkToFit') == '1'

    @shrink_to_fit.setter
    def shrink_to_fit(self, value: bool):
        self._xf.put_child_attrib('alignment', {'shrinkToFit': '1' if value else None})
        self._xf.remove_if_empty('alignment')

    @property
    def text_direction(self) -> Optional[AnyStr]:
        order = self._xf.get_child_attrib_value('alignment', 'readingOrder')
        if order == '1':
            return 'left-to-right'
        elif order == '2':
            return 'right-to-left'
        return order

    @text_direction.setter
    def text_direction(self, value: Optional[str]):
        order = None
        if value == 'left-to-right':
            order = '1'
        elif value == 'right-to-left':
            order = '2'
        self._xf.put_child_attrib('alignment', {'readingOrder': order})
        self._xf.remove_if_empty('alignment')

    def _get_text_rotation(self) -> Optional[float]:
        return try_parse(float, self._xf.get_child_attrib_value('alignment', 'textRotation'))

    def _set_text_rotation(self, value: Optional[float]):
        self._xf.put_child_attrib('alignment', {'textRotation':f'{value}' if value else None})
        self._xf.remove_if_empty('alignment')

    @property
    def text_rotation(self) -> Optional[float]:
        rotation = self._get_text_rotation()
        if rotation is None:
            return None
        if rotation > 90:
            rotation = 90 - rotation
        return rotation

    @text_rotation.setter
    def text_rotation(self, value: Optional[float]):
        if value is not None:
            if value < 0:
                value = 90 - value
        self._set_text_rotation(value)

    @property
    def angle_text_counter_clockwise(self) -> bool:
        return self._get_text_rotation() == 45

    @angle_text_counter_clockwise.setter
    def angle_text_counter_clockwise(self, value: bool):
        self._set_text_rotation(45 if value else None)

    @property
    def angle_text_clockwise(self) -> bool:
        return self._get_text_rotation() == 135

    @angle_text_clockwise.setter
    def angle_text_clockwise(self, value: bool):
        self._set_text_rotation(135 if value else None)

    @property
    def rotate_text_up(self) -> bool:
        return self._get_text_rotation() == 90

    @rotate_text_up.setter
    def rotate_text_up(self, value: bool):
        self._set_text_rotation(90 if value else None)

    @property
    def rotate_text_down(self) -> bool:
        return self._get_text_rotation() == 180

    @rotate_text_down.setter
    def rotate_text_down(self, value: bool):
        self._set_text_rotation(180 if value else None)

    @property
    def vertical_text(self) -> bool:
        return self._get_text_rotation() == 255

    @vertical_text.setter
    def vertical_text(self, value: bool):
        self._set_text_rotation(255 if value else None)    

    @property
    def fill(self) -> Optional[Fill]:
        pattern_fill = self._fill.find_by_localname('patternFill')
        gradient_fill = self._fill.find_by_localname('gradientFill')
        pattern_type = pattern_fill.get_attrib_value('patternType') if pattern_fill else None
        if pattern_type == 'solid':
            return SolidFile(self._get_color(pattern_fill, 'fgColor'))
        elif pattern_type:
            return PatternFill(pattern_type, 
                               self._get_color(pattern_fill, 'fgColor'),
                               self._get_color(pattern_fill, 'bgColor'))
        elif gradient_fill:
            gradient_type = gradient_fill.get_attrib_value('type') or 'linear'
            stops: List[Stop] = []
            for child in gradient_fill:
                pos = child.get_attrib_value('position')
                if pos:
                    stops.append(Stop(pos, self._get_color(child, 'color')))
            fill = GradientFill(gradient_type, stops)
            if gradient_type == 'linear':
                fill.angle = gradient_fill.get_attrib_value('degree')
            else:
                fill.left = gradient_fill.get_attrib_value('left')
                fill.right = gradient_fill.get_attrib_value('right')
                fill.top = gradient_fill.get_attrib_value('top')
                fill.bottom = gradient_fill.get_attrib_value('bottom')
            return fill
        return None

    @fill.setter
    def fill(self, value: Fill):
        self._fill.clear()
        if isinstance(value, SolidFile):
            pattern_fill = XmlElement.new('patternFill', {'patternType': 'solid'})
            self._set_color(pattern_fill, 'fgColor', value.color)
            self._fill.append(pattern_fill)
        elif isinstance(value, PatternFill):
            pattern_fill = XmlElement.new('patternFill', {'patternType': value.type})
            self._set_color(pattern_fill, 'fgColor', value.foreground)
            self._set_color(pattern_fill, 'bgColor', value.background)
            self._fill.append(pattern_fill)
        elif isinstance(value, GradientFill):
            gradient_fill = XmlElement.new('gradientFill')
            gradient_fill.put_attrib({
                'type': 'path' if value.type == 'path' else None,
                'left': value.left,
                'right': value.right,
                'top': value.top,
                'bottom': value.bottom,
                'degree': value.angle
            })
            for stop in value.stops:
                elem = XmlElement.new('stop', {'position':stop.position})
                self._set_color(elem, 'color', stop.color)
                gradient_fill.append(elem)
            self._fill.append(gradient_fill)



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
