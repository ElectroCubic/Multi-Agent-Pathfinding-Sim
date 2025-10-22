class Node:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.parent, self.g, self.h = None, float('inf'), float('inf')
        self.wall = False

    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)

    def __repr__(self):
        return f"Node({self.x}, {self.y})"
