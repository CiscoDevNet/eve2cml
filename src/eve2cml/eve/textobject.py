import logging
from typing import List

from bs4 import BeautifulSoup

from .decode import decode_data

_LOGGER = logging.getLogger(__name__)


def parse_style(style_string):
    style_dict = {}
    style_pairs = style_string.split(";")
    for pair in style_pairs:
        if pair.strip():  # Skip empty strings
            key, value = pair.split(":")
            style_dict[key.strip()] = value.strip()
    return style_dict


class TextObject:
    def __init__(self, id: str, name: str, obj_type: str, data=""):
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

    def obj_style_summary(self):

        def has_style(tag):
            has = tag.has_attr("style")
            return has

        if self._data is None or self._data.div is None:
            return {}

        style = self._data.div.find_all(has_style)
        styles = {}
        for el in style:
            el_style = parse_style(el["style"])
            styles = {**styles, **el_style}
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
        return int(self._div_style["left"].strip("px"))

    @property
    def top(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style["top"].strip("px"))

    @property
    def z_index(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style["z-index"])

    def __str__(self) -> str:
        return f"Text ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, Strings: {self.strings}, Data: {self.prettify()}, Pos: {self.left}/{self.top}/{self.z_index}"

    @classmethod
    def parse(cls, lab, path) -> List["TextObject"]:
        text_objects: List[TextObject] = []
        # for text_elem in lab.findall(".//objects/textobjects/textobject"):
        for text_elem in lab.findall(path):
            text_object = TextObject(
                id=text_elem.attrib.get("id") or "",
                name=text_elem.attrib.get("name") or "",
                obj_type=text_elem.attrib.get("type") or "",
            )
            data = text_elem.find("data")
            if data is not None and data.text:
                text_object.data = data.text
            text_objects.append(text_object)
        return text_objects

    def as_cml_dict(self):
        if self.obj_type == "text":
            if not len(self.strings) > 0:
                _LOGGER.warn("not a real text object")
                return None

            _LOGGER.info("procssing TEXT")
            style_summary = self.obj_style_summary()
            # _LOGGER.info("summary %s", style_summary)
            color = style_summary.get("color", "#808080")
            text_size = style_summary.get("font-size", "16px")
            background_color = style_summary.get("background-color", "#00000000")
            font_family = style_summary.get("font-family", "serif")
            return {
                "border_color": background_color,
                "border_style": "",
                "color": color,
                "rotation": 0,
                "text_bold": False,
                "text_content": self.strings,
                "text_font": font_family,
                "text_italic": False,
                "text_size": int(text_size.strip("px")),
                "text_unit": "pt",
                "thickness": 1,
                "type": "text",
                "x1": self.left,
                "y1": self.top,
                "z_index": self.z_index,
            }

        elif self.obj_type == "square":
            _LOGGER.info("procssing SQUARE")
            summary = {**self.obj_style_summary(), **self._data.div.svg.rect.attrs}
            _LOGGER.info(
                "style %s,%d,%d,%d", summary, self.top, self.left, self.z_index
            )
            return {
                "border_color": summary.get("stroke", "#808080FF"),
                "border_radius": int(round(float(summary.get("rx", "0")))),
                "border_style": summary.get("bla", ""),
                "color": summary.get("stroke", "#808080FF"),
                "thickness": int(summary.get("stroke-width", "1")),
                "type": "rectangle",
                "x1": self.left,
                "y1": self.top,
                "x2": int(round(float(summary.get("width", "80")))),
                "y2": int(round(float(summary.get("height", "80")))),
                "z_index": self.z_index,
            }
        elif self.obj_type == "circle":
            _LOGGER.info("procssing CIRCLE")
            summary = {**self.obj_style_summary(), **self._data.div.svg.ellipse.attrs}
            _LOGGER.info(
                "style %s,%d,%d,%d", summary, self.top, self.left, self.z_index
            )
            return {
                "border_color": summary.get("stroke", "#808080FF"),
                "border_style": summary.get("bla", ""),
                "color": summary.get("stroke", "#808080FF"),
                "thickness": int(summary.get("stroke-width", "1")),
                "type": "ellipse",
                "x1": self.left,
                "y1": self.top,
                "x2": 2 * int(round(float(summary.get("rx", "80")))),
                "y2": 2 * int(round(float(summary.get("ry", "80")))),
                "z_index": self.z_index,
            }
        else:
            _LOGGER.warn("object type %s", self.obj_type)
        return None
