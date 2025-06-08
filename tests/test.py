from src.KdTree import KdTree
from src.Establishment import Establishment
from src.Rectangle import Rectangle
import time

with open("input.txt") as file:
    n = int(file.readline())

    points = []
    for i in range(n):
        x, y = map(float, file.readline().split())
        points.append(Establishment(i, x, y, "data/complete_bar_data.csv"))

    q = int(file.readline())
    queries = []
    for _ in range(q):
        query = list(map(float, file.readline().split()))
        queries.append(query)

tree = KdTree(points)

start = time.time()
for query in queries:
    found = tree.query(Rectangle(*query))
    print(len(found))
    for point in found:
        print(f"{point.x} {point.y}")

end = time.time()
# print(f"{end - start:.4f}")