__author__ = 'fopitz'
import random
from cell import Cell

class Plate():
    def __init__(self, first_point):

        self.cells = []

        self.center = first_point
        self.boundaries = []

        self.drift = None
        self.spin = None

        self.is_oceanic = random.choice([False, True])

        if self.is_oceanic:
            # If the plate is oceanic set the height to some negative value
            self.elevation = random.randint(-50,0)
        else:
            self.elevation = random.randint(0,50)

        self.add_cell(first_point)


    def add_cell(self, coordinate):
        self.cells.append(Cell(coordinate, self.elevation))
