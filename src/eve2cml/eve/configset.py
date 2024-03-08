from typing import List
from xml.etree.ElementTree import Element

from .config import Config


class ConfigSet:
    def __init__(self, id: int, name: str, configs: List[Config]):
        self.id = id
        self.name = name
        self.configs = configs

    def __str__(self):
        return f"Config Set ID: {self.id}, Name: {self.name}, Contained Configs: {self.configs}"

    @classmethod
    def parse(cls, lab: Element, path) -> List["ConfigSet"]:
        configsets: List[ConfigSet] = []
        for configset_elem in lab.findall(path):
            configset = ConfigSet(
                id=int(configset_elem.attrib.get("id", 0)),
                name=configset_elem.attrib.get("name", "unknown"),
                configs=Config.parse(configset_elem, "config"),
            )
            configsets.append(configset)
        return configsets
