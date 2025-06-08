import random

def generate_test_file(filename="input.txt", n_points=10, coord_range=(-100, 100)):
    with open(filename, "w") as f:
        f.write(f"{n_points}\n")
        for _ in range(n_points):
            x = random.randint(coord_range[0], coord_range[1])
            y = random.randint(coord_range[0], coord_range[1])
            f.write(f"{x} {y}\n")
        
        f.write(f"{n_points}\n")
        for _ in range(n_points):
            x0 = random.randint(coord_range[0], coord_range[1])
            x1 = random.randint(coord_range[0], coord_range[1])
            y0 = random.randint(coord_range[0], coord_range[1])
            y1 = random.randint(coord_range[0], coord_range[1])
            f.write(f"{min(x0, x1)} {max(x0, x1)} {min(y0, y1)} {max(y0, y1)}\n")


generate_test_file(n_points=100)