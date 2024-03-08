from typing import List
from xml.etree.ElementTree import Element

from .decode import decode_data


class Config:
    def __init__(self, id: int, data: str):
        self.id = id
        self.data = data
        self._data: str

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: str):
        self._data = decode_data(value)

    def __str__(self):
        return f"Config ID: {self.id}, Data: {self.data}"

    @classmethod
    def parse(cls, lab: Element, path) -> List["Config"]:
        configs: List[Config] = []
        for config_elem in lab.findall(path):
            config = Config(
                id=int(config_elem.attrib.get("id", 0)), data=config_elem.text or ""
            )
            configs.append(config)
        return configs
