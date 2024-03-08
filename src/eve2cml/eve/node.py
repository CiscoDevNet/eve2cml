import logging
from typing import List
from xml.etree.ElementTree import Element

from . import Interface

_LOGGER = logging.getLogger(__name__)


class Node:
    def __init__(
        self,
        id: int,
        name: str,
        obj_type="",
        template="",
        image="",
        console="",
        cpu=0,
        cpulimit=0,
        ram=0,
        ethernet=0,
        uuid="",
        firstmac="",
        qemu_options="",
        qemu_version="",
        qemu_arch="",
        delay=0,
        sat=0,
        icon="",
        config="",
        left=0,
        top=0,
        e0dhcp="",
        interfaces: List[Interface] = [],
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

    def as_cml_dict(self, node_id, lab):
        node_definition, override = lab.mapper.node_def(
            self.obj_type, self.template, self.image
        )

        temp_list: List[Interface] = []
        prev = 0
        for idx, iface in enumerate(self.interfaces):
            delta = iface.slot - prev
            for idx2 in range(delta):
                temp_list.append(
                    Interface(
                        id=idx + idx2,
                        obj_type=self.obj_type,
                        network_id=999999,
                        name="filler",
                        slot=idx + idx2,
                    )
                )
            temp_list.append(iface)
            prev = iface.slot + 1

        iface_count = len(temp_list)
        iface_diff = int(self.ethernet) - iface_count
        if iface_diff > 0:
            _LOGGER.warning("Filler interfaces needed %s, %s, %d", self.id, self.name, iface_diff)
            for iface_idx in range(iface_diff):
                id = iface_count + iface_idx
                temp_list.append(
                    Interface(
                        id=id,
                        obj_type=self.obj_type,
                        network_id=999999,
                        slot=id,
                        name="doesntmatterhere",
                    )
                )

        _LOGGER.info("Serializing %s %s", self.name, self.id)
        return {
            "id": f"n{node_id}",
            "boot_disk_size": None,
            "configuration": lab.objects.get_config(self.config, self.id),
            "cpu_limit": 100 - int(self.cpulimit) if self.cpulimit else None,
            "cpus": int(self.cpu) if (self.cpu and not override) else None,
            "data_volume": None,
            "hide_links": False,
            "label": self.name,
            "node_definition": node_definition,
            "ram": int(self.ram) if (self.ram and not override) else None,
            "tags": [],
            "x": int(self.left),
            "y": int(self.top),
            "interfaces": [
                iface.as_cml_dict(idx, node_definition, lab)
                for idx, iface in enumerate(temp_list)
            ],
        }

    @classmethod
    def parse(cls, lab: Element) -> List["Node"]:
        nodes: List[Node] = []
        for node_elem in lab.findall(".//node"):
            id = int(node_elem.attrib.get("id", 0))
            obj_type = node_elem.attrib.get("type", "unknown")
            node = Node(
                id=id,
                name=node_elem.attrib.get("name", "unknown"),
                obj_type=obj_type,
                template=node_elem.attrib.get("template", "unknown"),
                image=node_elem.attrib.get("image", "unknown"),
                console=node_elem.attrib.get("console", "unknown"),
                cpu=int(node_elem.attrib.get("cpu", 0)),
                cpulimit=int(node_elem.attrib.get("cpulimit", 0)),
                ram=int(node_elem.attrib.get("ram", 0)),
                ethernet=int(node_elem.attrib.get("ethernet", 0)),
                uuid=node_elem.attrib.get("uuid", ""),
                firstmac=node_elem.attrib.get("firstmac", ""),
                qemu_options=node_elem.attrib.get("qemu_options", ""),
                qemu_version=node_elem.attrib.get("qemu_version", ""),
                qemu_arch=node_elem.attrib.get("qemu_arch", ""),
                delay=int(node_elem.attrib.get("delay", 0)),
                sat=int(node_elem.attrib.get("sat", 0)),
                icon=node_elem.attrib.get("icon", ""),
                config=node_elem.attrib.get("config", ""),
                left=int(node_elem.attrib.get("left", 0)),
                top=int(node_elem.attrib.get("top", 0)),
                e0dhcp=node_elem.attrib.get("e0dhcp", ""),
                interfaces=Interface.parse(
                    id, obj_type, node_elem.findall("interface")
                ),
            )
            nodes.append(node)
        return nodes
