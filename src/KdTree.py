from src.Establishment import Establishment
from src.Rectangle import Rectangle
from src.Node import Node

class KdTree:
    def __init__(self, points: list[Establishment]):
        self._root = self._build(points)
        
    def _build(self, points: list[Establishment], axis: bool = 0):
        if not points:
            return None
        
        node = Node(points)

        if node.all_equal():
            return node

        left, right = node.split_by_median(axis)
        node.left = self._build(left, not axis)
        node.right = self._build(right, not axis)
        return node
    
    def _recursion(self, node: Node, range: Rectangle):
        if node is None or not range.intersect(node.range):
            return []

        if range.fully_contained(node.range):
            return node.points
        
        return self._recursion(node.left, range) + self._recursion(node.right, range)

    def query(self, range: Rectangle) -> list[Establishment]:
        return self._recursion(self._root, range)