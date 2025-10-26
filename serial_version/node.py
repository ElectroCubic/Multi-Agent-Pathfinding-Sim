class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.wall = False
        self.parent = None
        self.g = float('inf')
        self.h = float('inf')

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self):
        return f"Node({self.x}, {self.y})"
