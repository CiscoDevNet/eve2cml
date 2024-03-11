import json
import logging
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional

from . import map_data as md

_LOGGER = logging.getLogger(__name__)


class CMLdef:
    def __init__(
        self, node_def: str, image_def: Optional[str] = None, override: bool = False
    ):
        self.node_def = node_def
        self.image_def = image_def
        self.override = override

    def __repr__(self):
        return "{}(node_def={}, image_def={}, override={})".format(
            self.__class__.__name__,
            self.node_def,
            self.image_def,
            self.override,
        )

    def as_dict(self):
        return {
            "node_def": self.node_def,
            "image_def": self.image_def,
            "override": self.override,
        }


class Eve2CMLmapper:
    def __init__(self):
        self.map: Dict[str, CMLdef] = {}
        self.unknown_type: str = ""
        self.interface_lists: Dict[str, List[str]] = {}

    def as_dict(self):
        return {
            "map": {k: v.as_dict() for k, v in self.map.items()},
            "unknown_type": self.unknown_type,
            "interface_lists": self.interface_lists,
        }

    def dump(self, filename: str):
        with open(filename, "w") as fh:
            return json.dump(self.as_dict(), fh, indent=2)

    @classmethod
    def load(cls, filename="") -> "Eve2CMLmapper":

        map_data = json.loads(resources.read_text(md, "default.json"))

        map_file = Path(filename)
        if map_file.is_file():
            with open(map_file, "r") as fh:
                map_data = json.load(fh)
            _LOGGER.warning("custom mapper loaded: %s", filename)
        else:
            if filename:
                _LOGGER.warning("mapper provided but not found: %s", filename)

        mapper = Eve2CMLmapper()
        mapper.unknown_type = map_data.get("unknown_type", "")
        mapper.interface_lists = map_data.get("interface_lists", {})
        for key, value in map_data.get("map", {}).items():
            mapper.map[key] = CMLdef(**value)

        return mapper

    def node_def(self, obj_type: str, template: str, image: str) -> CMLdef:
        found = self.map.get(f"{obj_type}:{template}:{image}")
        if not found:
            found = self.map.get(f"{obj_type}:{template}")
            if not found:
                _LOGGER.warn("Unmapped node type %s %s %s", obj_type, template, image)
                return CMLdef(self.unknown_type, None, True)
        return found

    def cml_iface_label(self, slot: int, node_def: str, label: str) -> str:
        interfaces = self.interface_lists.get(node_def)
        if interfaces is None:
            _LOGGER.warning("No mapping: %s %d", node_def, slot)
            return label
        return interfaces[slot]
