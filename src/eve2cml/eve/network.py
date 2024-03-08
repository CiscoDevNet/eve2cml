from typing import List
from xml.etree.ElementTree import Element


class Network:
    def __init__(self, id: int, obj_type: str, name: str, top: int, left: int):
        self.id = id
        self.obj_type = obj_type
        self.name = name
        self.left = left
        self.top = top
        # ignored for the moment
        self.style = "Solid"
        self.linkstyle = "Straight"
        self.color = ""
        self.label = ""
        self.visibility = "0"
        self.icon = "lan.png"

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.obj_type}"

    @classmethod
    def parse(cls, lab: Element) -> List["Network"]:
        networks: List[Network] = []
        for network_elem in lab.findall(".//networks/network"):
            network = Network(
                id=int(network_elem.attrib.get("id", 0)),
                obj_type=network_elem.attrib.get("type", "unknown"),
                name=network_elem.attrib.get("name", ""),
                top=int(network_elem.attrib.get("top", 0)),
                left=int(network_elem.attrib.get("left", 0)),
            )
            networks.append(network)
        return networks
