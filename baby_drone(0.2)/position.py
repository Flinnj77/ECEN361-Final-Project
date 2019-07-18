import math


class Position:

    def __init__(self):
        self.x = 0
        self.y = 0

    def movePosition(self, angle, magnitude):
        self.x = self.x + (magnitude * math.cos(angle))
        self.y = self.y + (magnitude * math.sin(angle))
