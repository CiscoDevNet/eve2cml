import logging
from typing import Tuple

import yaml

_LOGGER = logging.getLogger(__name__)


class Eve2CMLmapper:
    def __init__(self):
        self._map = {
            # type:template:image, image is optional
            # The boolean defines whether values for CPU, RAM, should be
            # overridden (e.g. set to 0 or Null in the output)
            "iol:iol": ("iol-xe", False),
            "qemu:csr1000vng": ("csr1000v", False),
            "qemu:nxosv9k": ("nxosv9000", False),
            "qemu:vios": ("iosv", False),
            "qemu:viosl2": ("iosvl2", False),
            "docker:docker:eve-gui-server:latest": ("desktop", True),
            "cml_ext_conn:cml_ext_conn": ("external_connector", True),
            "cml_ums:cml_ums": ("unmanaged_switch", True),
        }
        self._unknown_type = "server"
        self._interfacelists = {
            "external_connector": [
                "port",
            ],
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
            ],
            "csr1000v": [
                "GigabitEthernet1",
                "GigabitEthernet2",
                "GigabitEthernet3",
                "GigabitEthernet4",
                "GigabitEthernet5",
                "GigabitEthernet6",
                "GigabitEthernet7",
                "GigabitEthernet8",
                "GigabitEthernet9",
                "GigabitEthernet10",
                "GigabitEthernet11",
                "GigabitEthernet12",
                "GigabitEthernet13",
                "GigabitEthernet14",
                "GigabitEthernet15",
                "GigabitEthernet16",
                "GigabitEthernet17",
                "GigabitEthernet18",
                "GigabitEthernet19",
                "GigabitEthernet20",
                "GigabitEthernet21",
                "GigabitEthernet22",
                "GigabitEthernet23",
                "GigabitEthernet24",
                "GigabitEthernet25",
                "GigabitEthernet26",
            ],
            "nxosv9000": [
                "mgmt0",
                "Ethernet1/1",
                "Ethernet1/2",
                "Ethernet1/3",
                "Ethernet1/4",
                "Ethernet1/5",
                "Ethernet1/6",
                "Ethernet1/7",
                "Ethernet1/8",
                "Ethernet1/9",
                "Ethernet1/10",
                "Ethernet1/11",
                "Ethernet1/12",
                "Ethernet1/13",
                "Ethernet1/14",
                "Ethernet1/15",
                "Ethernet1/16",
                "Ethernet1/17",
                "Ethernet1/18",
                "Ethernet1/19",
                "Ethernet1/20",
                "Ethernet1/21",
                "Ethernet1/22",
                "Ethernet1/23",
                "Ethernet1/24",
                "Ethernet1/25",
                "Ethernet1/26",
                "Ethernet1/27",
                "Ethernet1/28",
                "Ethernet1/29",
                "Ethernet1/30",
                "Ethernet1/31",
                "Ethernet1/32",
                "Ethernet1/33",
                "Ethernet1/34",
                "Ethernet1/35",
                "Ethernet1/36",
                "Ethernet1/37",
                "Ethernet1/38",
                "Ethernet1/39",
                "Ethernet1/40",
                "Ethernet1/41",
                "Ethernet1/42",
                "Ethernet1/43",
                "Ethernet1/44",
                "Ethernet1/45",
                "Ethernet1/46",
                "Ethernet1/47",
                "Ethernet1/48",
                "Ethernet1/49",
                "Ethernet1/50",
                "Ethernet1/51",
                "Ethernet1/52",
                "Ethernet1/53",
                "Ethernet1/54",
                "Ethernet1/55",
                "Ethernet1/56",
                "Ethernet1/57",
                "Ethernet1/58",
                "Ethernet1/59",
                "Ethernet1/60",
                "Ethernet1/61",
                "Ethernet1/62",
                "Ethernet1/63",
                "Ethernet1/64",
            ],
            "desktop": [
                "eth0",
                "eth1",
                "eth2",
                "eth3",
            ],
            "server": [
                "eth0",
                "eth1",
                "eth2",
                "eth3",
                "eth4",
                "eth5",
                "eth6",
                "eth7",
                "eth8",
                "eth9",
            ],
            "unmanaged_switch": [
                "port0",
                "port1",
                "port2",
                "port3",
                "port4",
                "port5",
                "port6",
                "port7",
                "port8",
                "port9",
                "port10",
                "port11",
                "port12",
                "port13",
                "port14",
                "port15",
                "port16",
                "port17",
                "port18",
                "port19",
                "port20",
                "port21",
                "port22",
                "port23",
                "port24",
                "port25",
                "port26",
                "port27",
                "port28",
                "port29",
                "port30",
                "port31",
            ],
        }

    def dump(self):
        yaml.dump(self._map)

    def node_def(self, obj_type: str, template: str, image: str) -> Tuple[str, bool]:
        found = self._map.get(f"{obj_type}:{template}:{image}")
        if not found:
            found = self._map.get(f"{obj_type}:{template}")
            if not found:
                _LOGGER.warn("Unmapped node type %s %s %s", obj_type, template, image)
                return (self._unknown_type, True)
        return found

    def cml_iface_label(self, slot: int, node_def: str, label: str) -> str:
        interfaces = self._interfacelists.get(node_def)
        if interfaces is None:
            _LOGGER.warning("No mapping: %s %d", node_def, slot)
            return label
        return interfaces[slot]