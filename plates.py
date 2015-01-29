__author__ = 'fopitz'

import random
import math
import Queue

from PIL import Image

import constants
import helper
from vector import Vector
from plate import Plate


class Plates():
    def __init__(self, size = 1024, plate_count = 9):

        self.size = size
        # World_Map tracks which cells are populated during plate generation
        self.world_map = [[None for x in xrange(size)] for y in xrange(size)]
        # Plates tracks the plates. Each Plate object contains cells that track elevation
        self.plates = []
        self.image = im = Image.new('RGB', (self.size, self.size), 'white')

        self.plate_symbols = [(255,248,220),(165,42,42),(36,24,130),(47,79,47),(139,0, 139),(66,111,66),(255,105,180),(255,69,0), (170,170,15)]

        self.start_plates(plate_count)

        self.flood_fill()
        self.find_edges()

    def show_map(self):
        pixels = self.image.load()

        for n, plate in enumerate(self.plates):
            for cell in plate.cells.values():
                x, y = cell.coordinate
                pixels[x,y] = plate.plate_color
        self.image.show()

    def show_tempature_map(self):
        print 'creating temperature map image'
        pixels = self.image.load()

        for n, plate in enumerate(self.plates):
            for cell in plate.cells.values():
                x,y = cell.coordinate
                val = int(cell.temperature)
                val = (val + 15)*255/130
                pixels[x,y] = (val,val,val)

        print 'Temperature Map Created. Adding edges'
        for i, plate in enumerate(self.plates):
            for edge in plate.boundaries:
                x, y = edge
                if plate.is_oceanic:
                    pixels[x, y] = (0,0,100)
                else:
                    pixels[x, y] = (100, 0, 0)

        self.image.show()

    def start_plates(self, plate_count):
        size = self.size
        for p in xrange(plate_count):
            # random x, y point
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)

            # No perfectly overlapping plates
            while self.world_map[x][y] != None:
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1)

            plate = Plate(p, (x,y), self.plate_symbols[p])
            self.plates.append(plate)

    def flood_fill(self):
        q = Queue.Queue()
        for i, plate in enumerate(self.plates):
            q.put((plate.center, i))

        while not q.empty():
            coordinate, plate_num = q.get()
            x, y = coordinate
            if self.world_map[x][y] == None:
                self.plates[plate_num].add_cell((x, y)) # Add square to plate
                self.world_map[x][y] = plate_num # update world map

                if self.is_valid_and_empty(x-1, y) and random.randrange(2) == 0:
                    q.put(((x-1, y), plate_num))
                if self.is_valid_and_empty(x+1, y) and random.randrange(2) == 0:
                    q.put(((x+1, y), plate_num))
                if self.is_valid_and_empty(x, y-1) and random.randrange(2) == 0:
                    q.put(((x, y-1), plate_num))
                if self.is_valid_and_empty(x, y+1) and random.randrange(2) == 0:
                    q.put(((x, y+1), plate_num))
                if self.is_valid_and_empty(x-1, y+1) and random.randrange(2) == 0:
                    q.put(((x-1, y+1), plate_num))
                if self.is_valid_and_empty(x+1, y+1) and random.randrange(2) == 0:
                    q.put(((x+1, y+1), plate_num))
                if self.is_valid_and_empty(x-1, y-1) and random.randrange(2) == 0:
                    q.put(((x-1, y-1), plate_num))
                if self.is_valid_and_empty(x+1, y-1) and random.randrange(2) == 0:
                    q.put(((x+1, y-1), plate_num))

            q.task_done()

        # Scan for orphan cells and associate them with their most common neighbor
        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.world_map[x][y] is None:
                    q.put((x,y))

        while not q.empty():
            x, y = q.get()
            if self.world_map[x][y] == None:

                neighbors = []
                if self.bounds(x-1,y): neighbors.append(self.world_map[x-1][y])
                if self.bounds(x+1,y): neighbors.append(self.world_map[x+1][y])
                if self.bounds(x+1,y+1): neighbors.append(self.world_map[x+1][y+1])
                if self.bounds(x-1,y-1): neighbors.append(self.world_map[x-1][y-1])
                if self.bounds(x+1,y-1): neighbors.append(self.world_map[x+1][y-1])
                if self.bounds(x-1,y+1): neighbors.append(self.world_map[x-1][y+1])
                if self.bounds(x,y+1): neighbors.append(self.world_map[x][y+1])
                if self.bounds(x,y-1): neighbors.append(self.world_map[x][y-1])

                neighbors = filter(lambda a: a != None, neighbors)

                if len(neighbors) > 0:
                    plate_num = max(set(neighbors), key=neighbors.count)
                    self.world_map[x][y] = plate_num
                    self.plates[plate_num].add_cell((x,y))
                    q.task_done()
                else:
                    q.task_done()
                    q.put((x,y))



    def is_valid_and_empty(self, x, y):
        # Start by checking the bounds
        if self.bounds(x,y):
            return self.world_map[x][y] == None
        return False

    def bounds(self, x, y):
        if x >= 0 and x < self.size and y >= 0 and y < self.size:
            return True
        return False

    def find_edges(self):
        print 'finding edges'
        for plate in xrange(len(self.plate_symbols)):
            for cell in self.plates[plate].cells.values():
                x, y = cell.coordinate
                neighbors = self.valid_neighbors(cell.coordinate)
                for n in neighbors:
                    n_x, n_y = n
                    if self.world_map[x][y] != self.world_map[n_x][n_y]:
                        self.plates[plate].boundaries.append((x,y))
                        break


    def populate_temperature(self):
        print 'populating temperature'
        for y in xrange(self.size):
            for x in xrange(self.size):
                combined_heat, num_neighbors = self.surrounding_heat((x,y))

                fn_x = abs(y-(self.size/2))
                fn_m =  -1 * constants.TEMP_RANGE/ (self.size/2)
                fn_b = 255

                heat = fn_m * fn_x + fn_b # The liniar gradiant we apply goes from 0 to half the size with a temp range of -15 to 115
                basic_temp = (((combined_heat + heat)/(num_neighbors + 1)) + (random.randint(-1,1) * constants.TEMPERATURE_FLUX))

                plate = self.world_map[x][y]
                if self.plates[plate].is_oceanic:
                   basic_temp = helper.clamp(basic_temp - constants.OCEAN_TEMP, 0, 255)

                # Store temperature with the cell in the plate
                self.plates[plate].get_cell((x,y)).set_temperature(basic_temp)

    def normalize_temperatures(self):
        # normalize temp values:
        sum = 0.0
        for plate in self.plates:
            for cell in plate.cells.values():
                sum += cell.temperature
        avg = sum / (self.size**2)

        dif_sum = 0.0
        for plate in self.plates:
            for cell in plate.cells.values():
                dif_sum += (cell.temperature - sum)**2
        varience = dif_sum / (self.size**2)
        std_deviation = math.sqrt(varience)

        #apply std score
        for plate in self.plates:
            for cell in plate.cells.values():
                #print (self.temperature_map[x][y] - avg)/std_deviation
                cell.set_temperature((cell.temperature - avg)/std_deviation)

    def populate_wind(self):
        for plate in self.plates:
            for cell in plate.cells.values():
                x,y = cell.coordinate
                sum_vector = Vector()

                #check safety
                if x > 0: #left
                    sum_vector.add(self.heat_vector((x,y),(x-1,y), 180))
                if x < self.size -1: #right
                    sum_vector.add(self.heat_vector((x,y),(x+1,y), 0))
                if y > 0: #bottom
                    sum_vector.add(self.heat_vector((x,y),(x,y-1), 270))
                if y < self.size -1: #top
                    sum_vector.add(self.heat_vector((x,y),(x,y+1), 90))

                if x > 0 and y > 0: #upper left
                    sum_vector.add(self.heat_vector((x,y),(x-1,y-1), 135))
                if x > 0 and y < self.size -1: # upper right
                    sum_vector.add(self.heat_vector((x,y),(x-1,y+1), 45))
                if x < self.size -1 and y > 0: #lower left
                    sum_vector.add(self.heat_vector((x,y),(x+1,y-1), 225))
                if x < self.size-1 and y < self.size -1: #lower right
                    sum_vector.add(self.heat_vector((x,y),(x+1,y+1), 315))

                # Wind goes different directions in northern and southern hemispheres
                spin_direction = 180 if y - (self.size/2) > 0 else 0
                spin_v = Vector(abs((y - (self.size/2))) * constants.WINDSPEED, spin_direction)

                cell.set_windspeed(sum_vector.add(spin_v))

    def populate_moisture(self):
        None

    def heat_vector(self, cell, neighbor, direction):
        cell_x, cell_y = cell
        n_x, n_y = neighbor

        plate_num = self.world_map[cell_x][cell_y]
        c = self.plates[plate_num].get_cell(cell).temperature

        plate_num = self.world_map[n_x][n_y]
        n = self.plates[plate_num].get_cell(neighbor).temperature

        difference = c - n
        magnitude = abs(difference)

        heat_displacement_dir = abs(180-direction) if difference < 0 else direction

        heat_displacement_v = Vector(magnitude, heat_displacement_dir)

        return heat_displacement_v

    def valid_neighbors(self, point):
        neighbors = []
        x, y = point

        if x > 0: #left
            neighbors.append((x-1,y))
        if x < self.size -1: #right
            neighbors.append((x+1, y))
        if y > 0: #bottom
            neighbors.append((x,y-1))
        if y < self.size -1: #top
            neighbors.append((x, y+1))

        if x > 0 and y > 0: #upper left
            neighbors.append((x-1,y-1))
        if x > 0 and y < self.size -1: # upper right
            neighbors.append((x-1, y+1))
        if x < self.size -1 and y > 0: #lower left
            neighbors.append((x+1,y-1))
        if x < self.size-1 and y < self.size -1: #lower right
            neighbors.append((x+1, y+1))

        return neighbors

    def surrounding_heat(self, point):
        combined_heat = 0.0
        num_neighbors = 0
        neighbors = self.valid_neighbors(point)
        for n in neighbors:
            n_x, n_y = n
            plate_num = self.world_map[n_x][n_y]
            temp = self.plates[plate_num].get_cell(n).temperature
            if temp != None:
                combined_heat += temp
                num_neighbors += 1
        return combined_heat, num_neighbors

def main():
    import time
    start_time = time.clock()
    constants.init()
    plates = Plates()
    plates.show_map()
    print time.clock() - start_time, "seconds"
    plates.populate_temperature()
    #plates.normalize_temperatures() #might not be needed now
    plates.populate_wind()
    plates.show_tempature_map()

    print time.clock() - start_time, "seconds"

if __name__=='__main__':
    main()