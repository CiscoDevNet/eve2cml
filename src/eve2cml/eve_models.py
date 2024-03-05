import base64
import logging
from bs4 import BeautifulSoup
from typing import List

_LOGGER = logging.getLogger(__name__)


def decode_data(data):
    try:
        decoded = base64.b64decode(data).decode("utf-8")
    except Exception as exc:
        _LOGGER.exception("b64 decode %s", exc)
        decoded = data
    return decoded


def parse_style(style_string):
    style_dict = {}
    style_pairs = style_string.split(";")
    for pair in style_pairs:
        if pair.strip():  # Skip empty strings
            key, value = pair.split(":")
            style_dict[key.strip()] = value.strip()
    return style_dict


class TextObject:
    def __init__(self, id, name, type, data=None):
        self.id = id
        self.name = name
        self.type = type
        self._data = None
        self._div_style = None
        if data is not None:
            # self._data = BeautifulSoup(decode_data(data), 'html.parser')
            self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = BeautifulSoup(decode_data(value), "html.parser")
        div = self._data.find_all("div", class_="customShape")
        if len(div) > 0:
            self._div_style = parse_style(div[0]["style"])

    def prettify(self):
        if self.data is not None:
            return self.data.prettify()

    def strings(self):
        if self.data is not None:
            return "\n".join(self.data.stripped_strings)

    def left(self):
        if self._div_style is None:
            return 0
        return int(self._div_style["left"].strip("px"))

    def top(self):
        if self._div_style is None:
            return 0
        return int(self._div_style["top"].strip("px"))

    def zidx(self):
        if self._div_style is None:
            return 0
        return int(self._div_style["z-index"])

    def __str__(self):
        return f"Text ID: {self.id}, Name: {self.name}, Type: {self.type}, Strings: {self.strings()}, Data: {self.prettify()}, Pos: {self.left()}/{self.top()}/{self.zidx()}"


class Task:
    def __init__(self, id, name, type, data=None):
        self.id = id
        self.name = name
        self.type = type
        self.data = data

    def __str__(self):
        # return f"Task {self.id}, Name: {self.name}, Type: {self.type}, Data: {decode_data(self.data)}"
        return f"Task {self.id}, Name: {self.name}, Type: {self.type}"


class Config:
    def __init__(self, id, data):
        self.id = id
        self._data = decode_data(data)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = decode_data(value)

    def __str__(self):
        return f"Config ID: {self.id}, Data: {decode_data(self.data)}"


class ConfigSet:
    def __init__(self, id: str, name: str, configs: List[Config]):
        self.id = id
        self.name = name
        self.configs = configs

    def __str__(self):
        return f"Config Set ID: {self.id}, Name: {self.name}, Contained Configs: {self.configs}"


class Objects:
    def __init__(
        self,
        tasks: List[Task],
        configs: List[Config],
        configsets: List[ConfigSet],
        textobjects: List[TextObject],
    ):
        self.tasks = tasks
        self.configs = configs
        self.configsets = configsets
        self.textobjects = textobjects

    def __str__(self):
        return f"Tasks: {self.tasks}, Configs: {self.configs}, Config Sets: {self.configsets}, Text Objects: {self.textobjects}"

    def get_config(self, cfg_set: str, id: str):
        if cfg_set == "1":
            for config in self.configs:
                if config.id == id:
                    return config.data
            return ""
        for config_set in self.configsets:
            for config in config_set.configs:
                if config.id == id:
                    return config.data
        return ""


class Node:
    def __init__(
        self,
        id,
        name,
        type,
        template,
        image,
        console,
        cpu,
        cpulimit,
        ram,
        ethernet,
        uuid,
        firstmac,
        qemu_options,
        qemu_version,
        qemu_arch,
        delay,
        sat,
        icon,
        config,
        left,
        top,
        e0dhcp,
    ):
        self.id = id
        self.name = name
        self.type = type
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
        self.interfaces = []
        self.e0dhcp = e0dhcp

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.type}, Template: {self.template}, Image: {self.image}, Ethernet: {self.ethernet}"

    def as_cml_dict(self, idx, lab):
        return {
            "id": f"n{idx}",
            "bootdisksize": 0,
            "configuration": lab.objects.get_config(self.config, self.id),
            "cpu_limit": self.cpulimit,
            "cpus": self.cpu,
            "datavolume": 0,
            "hide_links": False,
            "label": self.name,
            "node_definition": "iosv",
            "ram": self.ram,
            "tags": [],
            "x": self.left,
            "y": self.top,
            "interfaces": [
                iface.as_cml_dict(idx) for idx, iface in enumerate(self.interfaces)
            ],
        }


class Interface:
    def __init__(
        self,
        id,
        name,
        type,
        network_id,
        labelpos,
        curviness,
        beziercurviness,
        midpoint,
        srcpos,
        dstpos,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.network_id = network_id
        self.labelpos = labelpos
        self.curviness = curviness
        self.beziercurviness = beziercurviness
        self.midpoint = midpoint
        self.srcpos = srcpos
        self.dstpos = dstpos

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.type}, NetID: {self.network_id}"

    def as_cml_dict(self, idx):
        return {
            "id": f"i{idx}",
            "label": self.name,
            "slot": idx,
            "type": "physical",
        }


class Network:
    def __init__(self, id, type, name, left, top):
        self.id = id
        self.type = type
        self.name = name
        self.left = left
        self.top = top
        # ignored for the moment
        self.style = "Solid"
        self.linkstyle = "Straight"
        self.color = ""
        self.label = ""
        self.visibility = "0"
        self.icon = "lan.png"

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Type: {self.type}"


class Topology:
    def __init__(self, nodes: List[Node], networks: List[Network]):
        self.nodes = nodes or []
        self.networks = networks or []

    def __str__(self):
        return f"Nodes: {self.nodes}, Networks: {self.networks}"


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

    def as_cml_dict(self):
        result = {}
        result["lab"] = {
            "description": "",
            "notes": "imported from EVE-NG",
            "title": self.name,
            "version": "0.1.0",
        }
        result["nodes"] = [
            node.as_cml_dict(idx, self) for idx, node in enumerate(self.topology.nodes)
        ]
        result["links"] = {}
        result["annotations"] = {}
        return result

    def __str__(self):
        return f"Lab: {self.name}, Version: {self.version}, Script Timeout: {self.scripttimeout}, Countdown: {self.countdown}, Lock: {self.lock}, SAT: {self.sat}"
