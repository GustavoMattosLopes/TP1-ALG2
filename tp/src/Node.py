from src.Establishment import Establishment
from src.Rectangle import Rectangle

class Node:
    def __init__(self, points: list[Establishment]):
        self.points = points
        self.left: Node = None
        self.right: Node = None

        xmin = ymin = float('inf')
        xmax = ymax = float('-inf')

        for p in points:
            xmin = min(xmin, p.x)
            xmax = max(xmax, p.x)
            ymin = min(ymin, p.y)
            ymax = max(ymax, p.y)

        self.range = Rectangle(xmin, xmax, ymin, ymax)

    def split_by_median(self, axis: bool):
        self.points.sort(key= lambda point: point.y if axis else point.x)
        median = (len(self.points) + 1) // 2
        return self.points[:median], self.points[median:]
    
    def all_equal(self):
        if not self.points:
            return True
        first = self.points[0]
        return all(p.x == first.x and p.y == first.y for p in self.points)