import logging
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from .config import Config
from .configset import ConfigSet
from .task import Task
from .textobject import TextObject

_LOGGER = logging.getLogger(__name__)


class Objects:
    def __init__(
        self,
        tasks: List[Task] = [],
        configs: List[Config] = [],
        configsets: List[ConfigSet] = [],
        textobjects: List[TextObject] = [],
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

    @classmethod
    def parse(cls, lab: Element, path: str, filename: str) -> "Objects":
        objects = lab.findall(path)
        if len(objects) == 0:
            return Objects()
        if len(objects) > 1:
            _LOGGER.warning(
                "more than one object in tree (%d) for %s", len(objects), filename
            )
        objects = objects[0]
        return Objects(
            Task.parse(objects, "tasks/task"),
            Config.parse(objects, "configs/config"),
            ConfigSet.parse(objects, "configsets/configset"),
            TextObject.parse(objects, "textobjects/textobject"),
        )

    def cml_annotations(self) -> List[Dict[str, Any]]:
        annotations: List[Dict[str, Any]] = []
        for object in self.textobjects:
            annotation_list = object.as_cml_annotations()
            for annotation in annotation_list:
                annotations.append(annotation)
        return annotations
