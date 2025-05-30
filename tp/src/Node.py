from src.Establishment import Establishment
from src.Rectangle import Rectangle

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
        if(len(points)==0):
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
        if x:
            points.sort(key= lambda establishment: establishment.x)
            return points[len(points)//2-(1 if len(points)%2 == 0 else 0)].x
        else:
            points.sort(key= lambda establishment: establishment.y)
            return points[len(points)//2-(1 if len(points)%2 == 0 else 0)].y
    
    def all_equals(self):
        for i in range(len(self.points)-1):
            if(self.points[i].x != self.points[i+1].x or self.points[i].y !=self.points[i+1].y):
                return False
        return True
    
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, points):
        self._points = points