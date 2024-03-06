import logging
from typing import Any, Dict, List, Tuple
from .interface import Interface
from .node import Node
from .objects import Objects
from .topology import Topology

from .mapper import Eve2CMLmapper


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
            "n2": f"n{self.to_id}",
            "i1": f"n{self.from_slot}",
            "i2": f"n{self.to_slot}",
            "label": self.label,
            "conditioning": {}
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
        topology: Topology,
        objects: Objects,
    ):
        self.name = name
        self.version = version
        self.scripttimeout = scripttimeout
        self.countdown = countdown
        self.lock = lock
        self.sat = sat
        self.topology = topology
        self.objects = objects
        self.mapper = Eve2CMLmapper()

    def as_cml_dict(self):
        result = {}
        result["lab"] = {
            "description": "",
            "notes": "imported from EVE-NG",
            "title": self.name,
            "version": "0.1.0",
        }
        result["links"] = self.cml_links()
        result["annotations"] = {}

        result["nodes"] = [
            node.as_cml_dict(idx, self) for idx, node in enumerate(self.topology.nodes)
        ]
        return result

    def __str__(self):
        return f"Lab: {self.name}, Version: {self.version}, Script Timeout: {self.scripttimeout}, Countdown: {self.countdown}, Lock: {self.lock}, SAT: {self.sat}"

    def _lookup_bridge_peers(self, network_id: str, name: str) -> CMLlink:
        found_ids: List[Tuple[int, int]] = []
        for node_idx, node in enumerate(self.topology.nodes):
            for slot, iface in enumerate(node.interfaces):
                if iface.network_id == network_id:
                    found_ids.append((node_idx, slot))
        if len(found_ids) != 2:
            _LOGGER.error("inconsistent topology %s", found_ids)
            raise RuntimeError
        return CMLlink(*found_ids[0], *found_ids[1], name)

    def cml_links(self) -> List[Dict[str, Any]]:
        links: List[Dict[str, Any]] = []
        for idx, network in enumerate(self.topology.networks):
            if network.obj_type == "bridge":
                pass
            elif network.obj_type.startswith("nat"):
                next_node_id = str(int(self.topology.nodes[-1].id)+1)
                ext_conn = Node(
                    id=next_node_id,
                    name=network.name,
                    obj_type="cml_ext_conn",
                    template="cml_ext_conn",
                    left=network.left,
                    top=network.top,
                    interfaces=[Interface(id="0", name="port", network_id=network.id)],
                )
                self.topology.nodes.append(ext_conn)
            else:
                _LOGGER.error("unhandled network type %s", network.obj_type)
            links.append(self._lookup_bridge_peers(network.id, network.name).as_cml_dict(idx))
        return links
