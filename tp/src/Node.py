from Establishment import Establishment
from Rectangle import Rectangle

class Node:
    def __init__(self, points, x):
        self._points = points
        self.median = self.compute_median(points, x)
        self.left:Node = None
        self.right:Node = None
        xmax = max(points, key = lambda p: p.x).x
        xmin = min(points, key = lambda p: p.x).x
        ymax = max(points, key = lambda p: p.y).y
        ymin = min(points, key = lambda p: p.y).y
        self.range = Rectangle(xmin, xmax, ymin, ymax)


    def compute_median(self, points:list[Establishment], x):
        if x:
            points.sort(key= lambda establishment: establishment.x)
            return points[len(points)//2].x - (1 if len(points)%2 == 0 else 0)
        else:
            points.sort(key= lambda establishment: establishment.y)
            return points[len(points)//2].y - (1 if len(points)%2 == 0 else 0)
    
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, points):
        self._points = points