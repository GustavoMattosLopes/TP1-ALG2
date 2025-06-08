with open("input.txt") as file:
    n = int(file.readline())

    points = []
    for i in range(n):
        x, y = map(float, file.readline().split())
        points.append((x, y))

    q = int(file.readline())
    queries = []
    for _ in range(q):
        query = list(map(float, file.readline().split()))
        queries.append(query)

with open("output.txt") as file:
    for query in queries:
        ans, out = set(), set()
        xmin, xmax, ymin, ymax = query
        for x, y in points:
            if xmin <= x <= xmax and ymin <= y <= ymax:
                ans.add((x, y))

        n = int(file.readline())
        if n:
            for _ in range(n):
                x, y = map(float, file.readline().split())
                out.add((x, y))

        if out != ans:
            print('ERRO: os pontos consultados não correspondem!')