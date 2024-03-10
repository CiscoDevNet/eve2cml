from typing import List, Optional
from xml.etree.ElementTree import Element

from .decode import decode_data


class Task:
    def __init__(self, id: int, name: str, obj_type: str, data: Optional[str] = None):
        self.id = id
        self.name = name
        self.obj_type = obj_type
        self.data = data

    def __str__(self):
        return f"Task {self.id}, Name: {self.name}, Type: {self.obj_type}, Data: {decode_data(self.data)}"
        # return f"Task {self.id}, Name: {self.name}, Type: {self.obj_type}"

    @classmethod
    def parse(cls, lab: Element, path: str) -> List["Task"]:
        tasks: List[Task] = []
        for task_elem in lab.findall(path):
            task = Task(
                id=int(task_elem.attrib.get("id", 0)),
                name=task_elem.attrib.get("name", "unknown"),
                obj_type=task_elem.attrib.get("type", "unknown"),
            )
            data = task_elem.find("data")
            if data is not None and data.text:
                task.data = data.text
            tasks.append(task)
        return tasks
