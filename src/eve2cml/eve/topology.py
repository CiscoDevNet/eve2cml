from typing import List

from .network import Network
from .node import Node


class Topology:
    def __init__(self, nodes: List[Node], networks: List[Network]):
        self.nodes = nodes or []
        self.networks = networks or []

    def __str__(self):
        return f"Nodes: {self.nodes}, Networks: {self.networks}"

    def next_node_id(self) -> int:
        return max([node.id for node in self.nodes]) + 1
