from typing import List


class Interface:
    def __init__(
        self,
        id,
        name,
        obj_type="",
        network_id="",
        labelpos="",
        curviness="",
        beziercurviness="",
        midpoint="",
        srcpos="",
        dstpos="",
    ):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self.network_id = network_id
        self.labelpos = labelpos
        self.curviness = curviness
        self.beziercurviness = beziercurviness
        self.midpoint = midpoint
        self.srcpos = srcpos
        self.dstpos = dstpos

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, NetID: {self.network_id}"

    def as_cml_dict(self, idx, node_def, lab):
        return {
            "id": f"i{idx}",
            "label": lab.mapper.cml_iface_label(idx, node_def, self.name),
            "slot": idx,
            "type": "physical",
        }

    @classmethod
    def parse(cls, elem) -> List["Interface"]:
        interfaces: List[Interface] = []
        for interface_elem in elem.findall("interface"):
            interface = Interface(
                id=interface_elem.attrib.get("id"),
                name=interface_elem.attrib.get("name"),
                obj_type=interface_elem.attrib.get("type"),
                network_id=interface_elem.attrib.get("network_id"),
                labelpos=interface_elem.attrib.get("labelpos"),
                curviness=interface_elem.attrib.get("curviness"),
                beziercurviness=interface_elem.attrib.get("beziercurviness"),
                midpoint=interface_elem.attrib.get("midpoint"),
                srcpos=interface_elem.attrib.get("srcpos"),
                dstpos=interface_elem.attrib.get("dstpos"),
            )
            interfaces.append(interface)
        return interfaces
