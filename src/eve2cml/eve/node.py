from typing import List

from . import Interface

class Node:
    def __init__(
        self,
        id,
        name,
        obj_type="",
        template="",
        image="",
        console="",
        cpu="",
        cpulimit="",
        ram="",
        ethernet="",
        uuid="",
        firstmac="",
        qemu_options="",
        qemu_version="",
        qemu_arch="",
        delay="",
        sat="",
        icon="",
        config="",
        left="",
        top="",
        e0dhcp="",
        interfaces: List[Interface]=[],
    ):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self.template = template
        self.image = image
        self.console = console
        self.cpu = cpu
        self.cpulimit = cpulimit
        self.ram = ram
        self.ethernet = ethernet
        self.uuid = uuid
        self.firstmac = firstmac
        self.qemu_options = qemu_options
        self.qemu_version = qemu_version
        self.qemu_arch = qemu_arch
        self.delay = delay
        self.sat = sat
        self.icon = icon
        self.config = config
        self.left = left
        self.top = top
        self.e0dhcp = e0dhcp
        self.interfaces = interfaces

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, X: {self.left}, Y: {self.top}, Template: {self.template}, Image: {self.image}, Ethernet: {self.ethernet}"

    def as_cml_dict(self, idx, lab):
        node_definition, override = lab.mapper.node_def(self.obj_type, self.template, self.image)
        iface_count = len(self.interfaces)
        iface_diff = int(self.ethernet) - iface_count
        if iface_diff > 0:
            for idx in range(iface_diff):
                self.interfaces.append(Interface(id=str(iface_count+idx), name="doesntmatterhere"))
        return {
            "id": f"n{idx}",
            "bootdisksize": None,
            "configuration": lab.objects.get_config(self.config, self.id),
            "cpu_limit": 100 - int(self.cpulimit) if self.cpulimit else None,
            "cpus": int(self.cpu) if (self.cpu and not override) else None,
            "datavolume": None,
            "hide_links": False,
            "label": self.name,
            "node_definition": node_definition,
            "ram": int(self.ram) if (self.ram and not override) else None,
            "tags": [],
            "x": int(self.left),
            "y": int(self.top),
            "interfaces": [
                iface.as_cml_dict(idx, node_definition, lab) for idx, iface in enumerate(self.interfaces)
            ],
        }

    @classmethod
    def parse(cls, lab) -> List["Node"]:
        nodes: List[Node] = []
        for node_elem in lab.findall(".//node"):
            node = Node(
                id=node_elem.attrib.get("id"),
                name=node_elem.attrib.get("name"),
                obj_type=node_elem.attrib.get("type"),
                template=node_elem.attrib.get("template"),
                image=node_elem.attrib.get("image"),
                console=node_elem.attrib.get("console"),
                cpu=node_elem.attrib.get("cpu"),
                cpulimit=node_elem.attrib.get("cpulimit"),
                ram=node_elem.attrib.get("ram"),
                ethernet=node_elem.attrib.get("ethernet"),
                uuid=node_elem.attrib.get("uuid"),
                firstmac=node_elem.attrib.get("firstmac"),
                qemu_options=node_elem.attrib.get("qemu_options"),
                qemu_version=node_elem.attrib.get("qemu_version"),
                qemu_arch=node_elem.attrib.get("qemu_arch"),
                delay=node_elem.attrib.get("delay"),
                sat=node_elem.attrib.get("sat"),
                icon=node_elem.attrib.get("icon"),
                config=node_elem.attrib.get("config"),
                left=node_elem.attrib.get("left"),
                top=node_elem.attrib.get("top"),
                e0dhcp=node_elem.attrib.get("e0dhcp"),
                interfaces=Interface.parse(node_elem),
            )
            nodes.append(node)
        return nodes
