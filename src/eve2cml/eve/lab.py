import logging
from typing import Any, Dict, List, Tuple

from .interface import Interface
from .mapper import Eve2CMLmapper
from .node import Node
from .objects import Objects
from .topology import Topology

_LOGGER = logging.getLogger(__name__)


class CMLlink:
    def __init__(
        self,
        from_id,
        from_slot,
        to_id,
        to_slot,
        label,
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
            "label": self.label,
            "conditioning": {},
        }


class Lab:
    def __init__(
        self,
        name,
        version,
        scripttimeout,
        countdown,
        lock,
        sat,
        description,
        topology: Topology,
        objects: Objects,
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
        self.mapper = Eve2CMLmapper()

    def as_cml_dict(self):
        result = {}
        result["lab"] = {
            "notes": self.description,
            "description": "Imported from EVE-NG via eve2cml",
            "title": self.name,
            "version": "0.1.0",
        }
        result["annotations"] = self.objects.cml_annotations()
        result["links"] = self.cml_links()
        result["nodes"] = [
            node.as_cml_dict(node.id, self) for node in self.topology.nodes
        ]

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

    def cml_links(self) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []

        current_link_id = 0

        # pass one, none-internal networks
        for network in self.topology.networks:
            _LOGGER.info("Processing network %d, %s", network.id, network.name)
            ifcelist = self._network_ifaces(network.id)
            num_ifaces = len(ifcelist)

            if network.obj_type == "bridge":

                if num_ifaces == 2:
                    _LOGGER.info("p2p")
                    from_iface = ifcelist[0]
                    to_iface = ifcelist[1]
                    links.append(
                        CMLlink(
                            from_iface.node_id,
                            from_iface.slot,
                            to_iface.node_id,
                            to_iface.slot,
                            network.name,
                        ).as_cml_dict(current_link_id)
                    )
                    current_link_id += 1
                elif num_ifaces > 2:
                    _LOGGER.info("ums")
                    next_node_id = self.topology.next_node_id()
                    ums_links = self._connect_internal_network(
                        next_node_id, network.id, network.name
                    )

                    obj_type = "cml_ums"
                    ums = Node(
                        id=next_node_id,
                        name=network.name,
                        obj_type=obj_type,
                        template=obj_type,
                        left=network.left,
                        top=network.top,
                        interfaces=[
                            Interface(
                                id=idx,
                                name=f"port{idx}",
                                obj_type=obj_type,
                                slot=idx,
                                network_id=network.id,
                            )
                            for idx in range(num_ifaces)
                        ],
                    )
                    ums.ethernet = 8 if num_ifaces < 8 else num_ifaces
                    self.topology.nodes.append(ums)
                    for link in ums_links:
                        links.append(link.as_cml_dict(current_link_id))
                        current_link_id += 1
                else:
                    _LOGGER.error("Can't deal with bridge with %d ifaces", num_ifaces)

            elif network.obj_type == "internal":
                _LOGGER.warning("Ignoring internal network %s", network.name)
                pass

            elif network.obj_type.startswith("nat"):
                _LOGGER.info("nat")
                if num_ifaces != 1:
                    _LOGGER.error("NAT interface has %d ifaces", num_ifaces)
                    continue
                next_node_id = self.topology.next_node_id()
                obj_type = "cml_ext_conn"
                ext_conn = Node(
                    id=next_node_id,
                    name=network.name,
                    obj_type=obj_type,
                    template=obj_type,
                    left=network.left,
                    top=network.top,
                    ethernet=1,
                    interfaces=[
                        Interface(
                            id=0,
                            obj_type=obj_type,
                            name="port",
                            network_id=network.id,
                            slot=0,
                        )
                    ],
                )
                self.topology.nodes.append(ext_conn)
                from_iface = ifcelist[0]
                links.append(
                    CMLlink(
                        from_iface.node_id,
                        from_iface.slot,
                        ext_conn.id,
                        0,
                        network.name,
                    ).as_cml_dict(current_link_id)
                )
                current_link_id += 1

            else:
                _LOGGER.warning("Unhandled network type %s", network.obj_type)

        return links