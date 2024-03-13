import logging
from typing import Any, Dict, List, Tuple

from ..mapper import Eve2CMLmapper
from .interface import Interface
from .network import Network
from .node import Node
from .objects import Objects
from .topology import Topology

_LOGGER = logging.getLogger(__name__)


class CMLlink:
    def __init__(
        self,
        from_id: int,
        from_slot: int,
        to_id: int,
        to_slot: int,
        label: str,
    ):
        self.from_id = from_id
        self.from_slot = from_slot
        self.to_id = to_id
        self.to_slot = to_slot
        self.label = label

    def as_cml_dict(self, idx: int):
        return {
            "id": f"l{idx}",
            "n1": f"n{self.from_id}",
            "i1": f"i{self.from_slot}",
            "n2": f"n{self.to_id}",
            "i2": f"i{self.to_slot}",
            "label": f"{self.label}-{idx}",
            "conditioning": {},
        }


class Lab:
    def __init__(
        self,
        name: str,
        version: str,
        scripttimeout: int,
        countdown: int,
        lock: bool,
        sat: int,
        description: str,
        topology: Topology,
        objects: Objects,
        filename: str,
        mapper: Eve2CMLmapper,
    ):
        self.name = name
        self.version = version
        self.scripttimeout = scripttimeout
        self.countdown = countdown
        self.lock = lock
        self.sat = sat
        self.description = description
        self.topology = topology
        self.objects = objects

        # conversion data
        self.mapper = mapper
        self.filename = filename

        self._links: List[Dict[str, Any]] = []
        self._current_link_id = 0

    def as_cml_dict(self):
        result: Dict[str, Any] = {}
        result["lab"] = {
            "notes": self.description,
            "description": f"Imported from {self.filename} via eve2cml converter",
            "title": self.name,
            "version": "0.1.0",
        }
        result["annotations"] = self.objects.cml_annotations()
        result["links"] = self.cml_links()
        result["nodes"] = [
            node.as_cml_dict(node.id, self) for node in self.topology.nodes
        ]

        labels = {node["label"] for node in result["nodes"]}
        if len(labels) != len(result["nodes"]):
            _LOGGER.warning(
                "node labels are not unique, this can not be imported into CML!"
            )

        return result

    def __str__(self):
        return f"Lab: {self.name}, Version: {self.version}, Script Timeout: {self.scripttimeout}, Countdown: {self.countdown}, Lock: {self.lock}, SAT: {self.sat}"

    def _network_ifaces(self, network_id: int) -> List[Interface]:
        interfaces: List[Interface] = []
        for node in self.topology.nodes:
            for iface in node.interfaces:
                if iface.network_id == network_id:
                    interfaces.append(iface)
        return interfaces

    def _connect_internal_network(
        self, ums_node_id: int, network_id: int, name: str
    ) -> List[CMLlink]:
        found_ids: List[Tuple[int, int]] = []
        for node in self.topology.nodes:
            for iface in node.interfaces:
                if iface.network_id == network_id:
                    found_ids.append((int(node.id), iface.slot))
        return [
            CMLlink(ums_node_id, idx, *found, name)
            for idx, found in enumerate(found_ids)
        ]

    def _insert_ext_conn(self, network: Network, config: str, offset=0) -> Node:
        next_node_id = self.topology.next_node_id()
        obj_type = "cml_ext_conn"
        ext_conn = Node(
            id=next_node_id,
            name=f"ext-{network.obj_type}-{network.name}",
            interfaces=[
                Interface(
                    id=0,
                    obj_type=obj_type,
                    name="port",
                    network_id=network.id,
                    slot=0,
                )
            ],
            obj_type=obj_type,
            template=obj_type,
            left=network.left,
            top=network.top - offset,
            ethernet=1,
        )
        ext_conn.cml_config = config
        self.topology.nodes.append(ext_conn)
        return ext_conn

    def _insert_ums(self, network: Network, num_ifaces: int):
        _LOGGER.info("ums")
        next_node_id = self.topology.next_node_id()
        ums_links = self._connect_internal_network(
            next_node_id, network.id, network.name
        )

        obj_type = "cml_ums"
        ums = Node(
            id=next_node_id,
            name=f"ums-{network.obj_type}-{network.name}",
            interfaces=[
                Interface(
                    id=idx,
                    name=f"port{idx}",
                    obj_type="ethernet",
                    slot=idx,
                    network_id=network.id,
                )
                for idx in range(num_ifaces)
            ],
            obj_type=obj_type,
            template=obj_type,
            left=network.left,
            top=network.top,
        )
        ums.ethernet = 8 if num_ifaces < 8 else num_ifaces
        self.topology.nodes.append(ums)
        for link in ums_links:
            self._links.append(link.as_cml_dict(self._current_link_id))
            self._current_link_id += 1

    def cml_links(self) -> List[Dict[str, Any]]:
        for network in self.topology.networks:
            _LOGGER.info("Processing network %d, %s", network.id, network.name)
            ifcelist = self._network_ifaces(network.id)
            num_ifaces = len(ifcelist)

            if network.obj_type == "bridge":
                if num_ifaces == 2:
                    _LOGGER.info("p2p")
                    from_iface = ifcelist[0]
                    to_iface = ifcelist[1]
                    self._links.append(
                        CMLlink(
                            from_iface.node_id,
                            from_iface.slot,
                            to_iface.node_id,
                            to_iface.slot,
                            network.name,
                        ).as_cml_dict(self._current_link_id)
                    )
                    self._current_link_id += 1
                elif num_ifaces > 2:
                    self._insert_ums(network, num_ifaces)
                else:
                    _LOGGER.error("Can't deal with bridge with %d ifaces", num_ifaces)

            elif network.obj_type.startswith("nat"):
                _LOGGER.info("nat")
                if num_ifaces != 1:
                    _LOGGER.error("NAT interface has %d ifaces", num_ifaces)
                    continue
                ext_conn = self._insert_ext_conn(network, config="nat")
                self._links.append(
                    CMLlink(
                        ifcelist[0].node_id,
                        ifcelist[0].slot,
                        ext_conn.id,
                        0,
                        network.name,
                    ).as_cml_dict(self._current_link_id)
                )
                self._current_link_id += 1

            elif network.obj_type.startswith("pnet"):
                _LOGGER.info("pnet")
                bridge_number = int(network.obj_type.lstrip("pnet"))
                ext_conn = self._insert_ext_conn(
                    network, config=f"bridge{bridge_number}", offset=64
                )
                self._insert_ums(network, num_ifaces + 1)

            elif network.obj_type == "internal":
                _LOGGER.warning("Ignoring internal network %s", network.name)

            else:
                _LOGGER.error(
                    "Unhandled network type %s (%d port(s)) in %s",
                    network.obj_type,
                    num_ifaces,
                    self.filename,
                )

        return self._links
