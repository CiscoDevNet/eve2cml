from typing import List

from .config import Config
from .configset import ConfigSet
from .task import Task
from .textobject import TextObject


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

    @classmethod
    def parse(cls, lab, path) -> "Objects":
        objects = lab.findall(path)[0]
        return Objects(
            Task.parse(objects, "tasks/task"),
            Config.parse(objects, "configs/config"),
            ConfigSet.parse(objects, "configsets/configset"),
            TextObject.parse(objects, "textobjects/textobject"),
        )
