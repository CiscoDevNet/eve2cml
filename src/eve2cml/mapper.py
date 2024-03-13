import io
import logging
import sys
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional

import yaml

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
        return f"{self.__class__.__name__}(node_def={self.node_def}, image_def={self.image_def}, override={self.override})"

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

    def dump(self, out: io.TextIOWrapper):
        return yaml.safe_dump(self.as_dict(), out, indent=2)

    @classmethod
    def load(cls, filename="") -> "Eve2CMLmapper":
        map_data = yaml.safe_load(resources.read_text(md, "default.yaml"))

        if filename:
            map_file = Path(filename)
            if map_file.is_file():
                with open(map_file) as fh:
                    try:
                        map_data = yaml.safe_load(fh)
                    except Exception as exc:
                        _LOGGER.critical("can't decode %s: %s", filename, exc)
                        sys.exit(1)
                _LOGGER.warning("custom mapper loaded: %s", filename)
            else:
                _LOGGER.error("mapper provided but not found. Using built-in mapper!")

        mapper = Eve2CMLmapper()
        mapper.unknown_type = map_data.get("unknown_type", "")
        mapper.interface_lists = map_data.get("interface_lists", {})
        for key, value in map_data.get("map", {}).items():
            mapper.map[key] = CMLdef(**value)

        return mapper

    def node_def(self, obj_type: str, template: str, image: str) -> CMLdef:
        lookup = f"{obj_type}:{template}:{image}"
        found = self.map.get(lookup)
        if not found:
            # special case for non-template images like IOL or Docker
            if image and template == obj_type:
                for key, cmldef in self.map.items():
                    if lookup.startswith(key):
                        return cmldef
            found = self.map.get(f"{obj_type}:{template}")
            if not found:
                _LOGGER.warning(
                    "Unmapped node type %s %s %s", obj_type, template, image
                )
                return CMLdef(self.unknown_type, None, True)
        return found

    def cml_iface_label(self, slot: int, node_def: str, label: str) -> str:
        interfaces = self.interface_lists.get(node_def)
        if interfaces is None:
            _LOGGER.warning("No mapping: %s %d", node_def, slot)
            return label
        return interfaces[slot]
