import logging
from typing import TYPE_CHECKING, List
from xml.etree.ElementTree import Element

from . import Interface

if TYPE_CHECKING:
    from .lab import Lab

_LOGGER = logging.getLogger(__name__)


class Node:
    def __init__(
        self,
        id: int,
        name: str,
        interfaces: List[Interface],
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
        config=0,
        left=0,
        top=0,
        e0dhcp="",
    ):
        self.id = id
        self.name = name
        self.interfaces = interfaces
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

        self.cml_hide_links = False
        self.cml_config = ""

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.obj_type}, X: {self.left}, Y: {self.top}, Template: {self.template}, Image: {self.image}, Ethernet: {self.ethernet}"

    def as_cml_dict(self, node_id: int, lab: "Lab"):
        nd_map = lab.mapper.node_def(self.obj_type, self.template, self.image)

        temp_list: List[Interface] = []
        prev_idx = 0
        prev_slot = 0
        _LOGGER.debug(self.interfaces)
        for idx, iface in enumerate(self.interfaces):
            delta = iface.slot - prev_slot
            _LOGGER.debug(
                "idx, slot, prev, delta %d/%d/%d/%d", idx, iface.slot, prev_slot, delta
            )
            for idx2 in range(delta):
                _LOGGER.debug(
                    "prepending filler interface id %d/%d", prev_idx, prev_slot + idx2
                )
                temp_list.append(
                    Interface(
                        id=prev_idx,
                        obj_type=self.obj_type,
                        network_id=999999,
                        name="filler",
                        slot=prev_slot + idx2,
                    )
                )
                prev_idx += 1
            iface.id = prev_idx
            temp_list.append(iface)
            prev_slot = iface.slot + 1
            prev_idx += 1

        _LOGGER.debug("list %s", temp_list)

        iface_count = len(temp_list)
        iface_diff = int(self.ethernet) - iface_count
        if iface_diff > 0:
            _LOGGER.info(
                "Filler interfaces needed for Node %d/%s, add %d",
                self.id,
                self.name,
                iface_diff,
            )
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

        # If there's no config then use the cml config (which also might be the
        # empty string)
        config = lab.objects.get_config(self.config, self.id) or self.cml_config

        _LOGGER.info("Serializing %s %s", self.name, self.id)
        return {
            "id": f"n{node_id}",
            "boot_disk_size": None,
            "configuration": config,
            "cpu_limit": 100 - int(self.cpulimit) if self.cpulimit else None,
            "cpus": int(self.cpu) if (self.cpu and not nd_map.override) else None,
            "data_volume": None,
            "hide_links": self.cml_hide_links,
            "label": self.name,
            "node_definition": nd_map.node_def,
            "image_definition": nd_map.image_def,
            "ram": int(self.ram) if (self.ram and not nd_map.override) else None,
            "tags": [],
            "x": int(self.left),
            "y": int(self.top),
            "interfaces": [
                iface.as_cml_dict(idx, nd_map.node_def, lab)
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
                interfaces=Interface.parse(
                    id, obj_type, node_elem.findall("interface")
                ),
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
                config=int(node_elem.attrib.get("config", 0)),
                left=int(node_elem.attrib.get("left", 0)),
                top=int(node_elem.attrib.get("top", 0)),
                e0dhcp=node_elem.attrib.get("e0dhcp", ""),
            )
            nodes.append(node)
        return nodes
