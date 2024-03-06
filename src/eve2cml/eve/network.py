from typing import List


class Network:
    def __init__(self, id: str, obj_type: str, name: str, top: str, left: str):
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
    def parse(cls, lab) -> List["Network"]:
        networks: List[Network] = []
        for network_elem in lab.findall(".//networks/network"):
            network = Network(
                id=network_elem.attrib.get("id"),
                obj_type=network_elem.attrib.get("type"),
                name=network_elem.attrib.get("name"),
                top=network_elem.attrib.get("top"),
                left=network_elem.attrib.get("left"),
            )
            networks.append(network)
        return networks
