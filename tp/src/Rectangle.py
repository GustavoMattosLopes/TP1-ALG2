class Rectangle:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def fully_contained(self, other: 'Rectangle') -> bool:  
        return (
            self.xmin <= other.xmin and 
            self.xmax >= other.xmax and 
            self.ymin <= other.ymin and
            self.ymax >= other.ymax
        )
    
    def intersect(self, other: 'Rectangle') -> bool:
        xmin = max(self.xmin, other.xmin)
        xmax = min(self.xmax, other.xmax)
        ymin = max(self.ymin, other.ymin)
        ymax = min(self.ymax, other.ymax)
        return (xmin <= xmax and ymin <= ymax)