import logging
import yaml
from typing import Tuple


_LOGGER = logging.getLogger(__name__)


class Eve2CMLmapper:
    def __init__(self):
        self._map = {
                "iol:iol": ("iol-xe", False),
                "qemu:vios": ("iosv", False),
                "qemu:viosl2": ("iosvl2", False),
                "docker:docker:eve-gui-server:latest": ("desktop", True),
                "cml_ext_conn:cml_ext_conn": ("external_connector", True),
        }
        self._unknown_type = "server"
        self._interfacelists = {
                "iol-xe": [
                  "Ethernet0/0",
                  "Ethernet0/1",
                  "Ethernet0/2",
                  "Ethernet0/3",
                  "Ethernet1/0",
                  "Ethernet1/1",
                  "Ethernet1/2",
                  "Ethernet1/3",
                  "Ethernet2/0",
                  "Ethernet2/1",
                  "Ethernet2/2",
                  "Ethernet2/3",
                  "Ethernet3/0",
                  "Ethernet3/1",
                  "Ethernet3/2",
                  "Ethernet3/3",
                ],
                "iosv": [
                  "GigabitEthernet0/0",
                  "GigabitEthernet0/1",
                  "GigabitEthernet0/2",
                  "GigabitEthernet0/3",
                  "GigabitEthernet0/4",
                  "GigabitEthernet0/5",
                  "GigabitEthernet0/6",
                  "GigabitEthernet0/7",
                  "GigabitEthernet0/8",
                  "GigabitEthernet0/9",
                  "GigabitEthernet0/10",
                  "GigabitEthernet0/11",
                  "GigabitEthernet0/12",
                  "GigabitEthernet0/13",
                  "GigabitEthernet0/14",
                  "GigabitEthernet0/15",
                ],
                "iosvl2": [
                  "GigabitEthernet0/0",
                  "GigabitEthernet0/1",
                  "GigabitEthernet0/2",
                  "GigabitEthernet0/3",
                  "GigabitEthernet1/0",
                  "GigabitEthernet1/1",
                  "GigabitEthernet1/2",
                  "GigabitEthernet1/3",
                  "GigabitEthernet2/0",
                  "GigabitEthernet2/1",
                  "GigabitEthernet2/2",
                  "GigabitEthernet2/3",
                  "GigabitEthernet3/0",
                  "GigabitEthernet3/1",
                  "GigabitEthernet3/2",
                  "GigabitEthernet3/3",
                ]

        }

    def dump(self):
        yaml.dump(self._map)

    def node_def(self, obj_type: str, template: str, image: str) -> Tuple[str, bool]:
        found = self._map.get(f"{obj_type}:{template}:{image}")
        if not found:
            found = self._map.get(f"{obj_type}:{template}")
            if not found:
                _LOGGER.warn("unmapped node type %s %s %s", obj_type, template, image)
                return (self._unknown_type, True)
        return found

    def cml_iface_label(self, slot: int, node_def: str, label: str) -> str:
        interfaces = self._interfacelists.get(node_def)
        if interfaces is None:
            return label
        return interfaces[slot]
