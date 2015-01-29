__author__ = 'fopitz'
import random
from cell import Cell

class Plate():
    def __init__(self, plate_id, first_point, plate_color):

        self.cells = {}

        self.plate_id = plate_id

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

        self.plate_color = plate_color


    def add_cell(self, coordinate):
        self.cells[coordinate] = Cell(coordinate, self.elevation)
        #print 'adding cell', coordinate, 'to plate ', self.plate_id

    def get_cell(self, coordinate):
        return self.cells[coordinate]