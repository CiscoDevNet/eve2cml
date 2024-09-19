import logging
import re
from functools import cached_property
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from bs4 import BeautifulSoup

from .decode import decode_data

_LOGGER = logging.getLogger(__name__)

# just a default color as a fallback
GRAY = "#808080FF"


def parse_style(style_string):
    style_dict = {}
    style_pairs = style_string.split(";")
    for pair in style_pairs:
        if pair.strip():  # Skip empty strings
            key, value = pair.split(":")
            style_dict[key.strip()] = value.strip()
    # _LOGGER.info("style %s %s", style_string, style_dict)
    return style_dict


def rgb_to_hex(rgb_string):
    # Split the RGB components and convert them to integers
    exp = r"rgba?\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})(?:,\s*(\d{1,3}))?\)"
    match = re.match(exp, rgb_string)
    if match:
        values = [255 if v is None else int(v) for v in match.groups()]
        for value in values:
            if value < 0 or value > 255:
                raise ValueError
        return f'#{"".join([f"{int(v):02x}" for v in values])}'.upper()
    raise ValueError


def color_convert(color: str) -> str:
    if color.startswith("rgb"):
        color = rgb_to_hex(color)
    if color.startswith("#") and len(color) == 7:
        return f"{color}FF"
    return color


def parse_rotate(rotate: str) -> int:
    exp = r"rotate\((\d{1,3})deg\)"
    match = re.match(exp, rotate)
    if match:
        return int(match.group(1))
    return 0


class TextObject:
    def __init__(self, id: int, name: str, obj_type: str, data=""):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self._data = None
        self._div = None
        self._div_style = None
        if data:
            self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = BeautifulSoup(decode_data(value), "html.parser")
        self._div = self._data.find_all("div", class_="customShape")
        if len(self._div) > 0:
            self._div_style = parse_style(self._div[0]["style"])

    @cached_property
    def style_summary(self):
        def has_style(tag):
            has = tag.has_attr("style")
            return has

        if self._data is None or self._data.div is None:
            return {}

        style = self._data.div.find_all(has_style)
        styles: Dict[str, str] = {}
        for el in style:
            el_style = parse_style(el["style"])
            styles = {**styles, **el_style}

        # Check out potential font tags for color information
        # This is quite a hack as there could be different colors in a text
        # object, also font sizes and what else...  Pretty much the Wild West.
        font_tags = self._data.div.find_all("font")
        if len(font_tags) > 0:
            # First color in list? Or the last... Guessing
            color = font_tags[0].attrs.get("color")
            if color is not None:
                styles["color"] = color
        return styles

    def prettify(self) -> str:
        if self.data is not None:
            return self.data.prettify()
        return ""

    @property
    def strings(self) -> str:
        if self.data is not None:
            return "\n".join(self.data.stripped_strings)
        return ""

    @property
    def left(self) -> int:
        if self._div_style is None:
            return 0
        return int(float(self._div_style["left"].strip("px")))

    @property
    def top(self) -> int:
        if self._div_style is None:
            return 0
        return int(float(self._div_style["top"].strip("px")))

    @property
    def width(self) -> int:
        if self._div_style is None:
            return 0
        value = self._div_style.get("width", "")
        # best guesses
        if value == "" or value == "auto":
            line_length = max([len(line) for line in self.strings.split("\n")])
            return int(
                line_length
                * 0.67
                * float(self.style_summary.get("font-size", "14").strip("px"))
            )
        return int(float(value.strip("px")))

    @property
    def height(self) -> int:
        if self._div_style is None:
            return 0
        value = self._div_style.get("height", "")
        # best guesses
        if value == "" or value == "auto":
            lines = self.strings.rstrip().count("\n") + 1
            return int(
                lines
                * 1.5
                * float(self.style_summary.get("font-size", "14").strip("px"))
            )
        return int(float(value.strip("px")))

    @property
    def z_index(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style.get("z-index", 0))

    @property
    def rotation(self) -> int:
        if self._div_style is None:
            return 0
        transform = self._div_style.get("transform")
        if transform is None:
            return 0
        return int(parse_rotate(transform))

    def __str__(self) -> str:
        return f"Text ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, Strings: {self.strings}, Data: {self.prettify()}, Pos: {self.left}/{self.top}/{self.z_index}"

    @classmethod
    def parse(cls, lab: Element, path: str) -> List["TextObject"]:
        text_objects: List[TextObject] = []
        for text_elem in lab.findall(path):
            text_object = TextObject(
                id=int(text_elem.attrib.get("id", 0)),
                name=text_elem.attrib.get("name") or "",
                obj_type=text_elem.attrib.get("type") or "",
            )
            data = text_elem.find("data")
            if data is not None and data.text:
                text_object.data = data.text
            text_objects.append(text_object)
        return text_objects

    def as_cml_annotations(self) -> List[Dict[str, Any]]:
        if self.obj_type == "text":
            if not len(self.strings) > 0:
                _LOGGER.info("Not a real text object, ignoring")
                return []

            _LOGGER.info("Procssing ID %d, TEXT", self.id)
            color = color_convert(self.style_summary.get("color", GRAY))
            text_size = self.style_summary.get("font-size", "16px")
            background_color = self.style_summary.get("background-color", "")
            if background_color:
                background_color = color_convert(background_color)
            font_family = self.style_summary.get("font-family", "serif")
            ret_val = [
                {
                    "border_color": "#FFFFFF00",
                    "border_style": "",
                    "color": color,
                    "rotation": self.rotation,
                    "text_bold": False,
                    "text_content": self.strings,
                    "text_font": font_family,
                    "text_italic": False,
                    "text_size": max(int(float(text_size.strip("px"))), 8),
                    "text_unit": "pt",
                    "thickness": 1,
                    "type": "text",
                    "x1": self.left,
                    "y1": self.top,
                    "z_index": self.z_index,
                }
            ]
            if background_color != "":
                ret_val.append(
                    {
                        "border_color": "#FFFFFF00",
                        "border_radius": 0,
                        "border_style": "",
                        "color": background_color,
                        # rotation works with 2.8+
                        "rotation": self.rotation,
                        "thickness": 1,
                        "type": "rectangle",
                        "x1": self.left,
                        "y1": self.top,
                        "x2": self.width,
                        "y2": self.height,
                        "z_index": self.z_index - 1,
                    }
                )
            return ret_val

        elif self.obj_type == "square":
            _LOGGER.info("Procssing ID %d, SQUARE", self.id)
            summary = {**self.style_summary, **self._data.div.svg.rect.attrs}  # type: ignore
            return [
                {
                    "border_color": color_convert(summary.get("stroke", GRAY)),
                    "border_radius": int(float(summary.get("rx", "0"))),
                    "border_style": summary.get("bla", ""),
                    "color": color_convert(summary.get("fill", GRAY)),
                    "thickness": max(int(float(summary.get("stroke-width", "1"))), 1),
                    # rotation works with 2.8+
                    "rotation": self.rotation,
                    "type": "rectangle",
                    "x1": self.left,
                    "y1": self.top,
                    "x2": float(summary.get("width", "80")),
                    "y2": float(summary.get("height", "80")),
                    "z_index": self.z_index,
                }
            ]

        elif self.obj_type == "circle":
            _LOGGER.info("Procssing ID %d, CIRCLE", self.id)
            summary = {**self.style_summary, **self._data.div.svg.ellipse.attrs}  # type: ignore
            rx = float(summary.get("rx", "80"))
            ry = float(summary.get("ry", "80"))
            return [
                {
                    "border_color": color_convert(summary.get("stroke", GRAY)),
                    "border_style": summary.get("bla", ""),
                    "color": color_convert(summary.get("stroke", GRAY)),
                    "thickness": max(int(float(summary.get("stroke-width", "1"))), 1),
                    # rotation works with 2.8+
                    "rotation": self.rotation,
                    "type": "ellipse",
                    "x1": rx + self.left,
                    "y1": ry + self.top,
                    "x2": rx,
                    "y2": ry,
                    "z_index": self.z_index,
                }
            ]
        else:
            _LOGGER.warning("Object type %s", self.obj_type)
        return []
