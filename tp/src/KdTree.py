from src.Establishment import Establishment
from src.Node import Node
from src.Rectangle import Rectangle

class KdTree:
    def __init__(self, points:list[Establishment]):
        self.root = self._build(points)
        
    def _build(self, points: list[Establishment], x = 0):
        if points is None:
            return []
        

        node = Node(points, x)
        median = node.median
        left = []
        right = []

        if node.all_equals():
            return node


        get_coord = lambda p: p.x if x else p.y
        for point in points:
            if(get_coord(point) <= median):
                left.append(point)
            else:
                right.append(point)

        node.left = self._build(left, not x)
        if len(right) > 0:
            node.right = self._build(right, not x)
        else:
            node.right = None
        return node

    def query(self, range:Rectangle):
        return self.recursion(node = self.root, range = range)
    
    def recursion(self, node: Node, range: Rectangle):
        if node is None:
            return []
                
        if not range.intersect(node.range):
            return []

        if range.fully_contained(node.range):
            return node.points
        
        return self.recursion(node.left, range) + self.recursion(node.right, range)