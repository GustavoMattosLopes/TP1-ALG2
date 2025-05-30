from kd_tree import KdTree
from Establishment import Establishment
from Rectangle import Rectangle

points = [Establishment(11, 4), Establishment(16, 20), Establishment(2, 2), Establishment(6, 3),
          Establishment(80, 6), Establishment(7, 50)]


tree = KdTree(points)

ans = tree.query(Rectangle(2, 8, 3, 51))

for e in ans:
    print(e)
