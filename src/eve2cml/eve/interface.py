from typing import List
from xml.etree.ElementTree import Element


class Interface:
    def __init__(
        self,
        id: int,
        name: str,
        obj_type: str,
        network_id: int,
        labelpos="",
        curviness="",
        beziercurviness="",
        midpoint="",
        srcpos="",
        dstpos="",
        node_id=0,
        slot=0,
    ):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self.network_id = network_id

        # ignored for the moment
        self.labelpos = labelpos
        self.curviness = curviness
        self.beziercurviness = beziercurviness
        self.midpoint = midpoint
        self.srcpos = srcpos
        self.dstpos = dstpos

        # private, for linking
        self.node_id = node_id
        self.slot = slot

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, NetID: {self.network_id}"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, slot={self.slot})"

    def as_cml_dict(self, idx, node_def, lab):
        # can likely remove the idx arg as the id should match the idx!
        assert self.id == idx
        return {
            # "id": f"i{self.id}",
            "id": f"i{idx}",
            "label": lab.mapper.cml_iface_label(self.slot, node_def, self.name),
            "slot": self.slot,
            "type": "physical",
        }

    @classmethod
    def parse(
        cls, node_id: int, obj_type: str, elem: List[Element]
    ) -> List["Interface"]:
        # special treatment for slots when type is IOL
        no_iol = obj_type != "iol"

        interfaces: List[Interface] = []
        for interface_elem in elem:
            id = int(interface_elem.attrib.get("id", "unknown"))
            interface = Interface(
                id=id,
                name=interface_elem.attrib.get("name", "unknown"),
                obj_type=interface_elem.attrib.get("type", "unknown"),
                network_id=int(interface_elem.attrib.get("network_id", 0)),
                labelpos=interface_elem.attrib.get("labelpos", ""),
                curviness=interface_elem.attrib.get("curviness", ""),
                beziercurviness=interface_elem.attrib.get("beziercurviness", ""),
                midpoint=interface_elem.attrib.get("midpoint", ""),
                srcpos=interface_elem.attrib.get("srcpos", ""),
                dstpos=interface_elem.attrib.get("dstpos", ""),
                node_id=node_id,
                slot=id if no_iol else ((id & 0xF) * 4) + (id >> 4),
            )
            interfaces.append(interface)
        return interfaces
