from typing import List

from .decode import decode_data


class Config:
    def __init__(self, id, data):
        self.id = id
        self._data = ""
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = decode_data(value)

    def __str__(self):
        return f"Config ID: {self.id}, Data: {self.data}"

    @classmethod
    def parse(cls, lab, path) -> List["Config"]:
        configs: List[Config] = []
        for config_elem in lab.findall(path):
            config = Config(id=config_elem.attrib.get("id"), data=config_elem.text)
            configs.append(config)
        return configs
