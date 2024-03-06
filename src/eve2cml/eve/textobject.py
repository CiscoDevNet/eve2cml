from typing import List

from bs4 import BeautifulSoup

from .decode import decode_data


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
        self._div_style = None
        if data:
            self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = BeautifulSoup(decode_data(value), "html.parser")
        div = self._data.find_all("div", class_="customShape")
        if len(div) > 0:
            self._div_style = parse_style(div[0]["style"])

    def prettify(self) -> str:
        if self.data is not None:
            return self.data.prettify()
        return ""

    def strings(self) -> str:
        if self.data is not None:
            return "\n".join(self.data.stripped_strings)
        return ""

    def left(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style["left"].strip("px"))

    def top(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style["top"].strip("px"))

    def zidx(self) -> int:
        if self._div_style is None:
            return 0
        return int(self._div_style["z-index"])

    def __str__(self) -> str:
        return f"Text ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, Strings: {self.strings()}, Data: {self.prettify()}, Pos: {self.left()}/{self.top()}/{self.zidx()}"

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
