from src.KdTree import KdTree
from src.Establishment import Establishment
from src.Rectangle import Rectangle

n = int(input())

points = []
for i in range(n):
    x, y = map(float, input().split())
    points.append(Establishment(i, x, y, None))

tree = KdTree(points)

q = int(input())
for _ in range(q):
    range = list(map(float, input().split()))
    found = tree.query(Rectangle(*range))
    print(len(found))
    for point in found:
        print(f"{point.x} {point.y}")