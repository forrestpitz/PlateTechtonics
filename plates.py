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
    def __init__(self, size = 512):

        self.size = size
        self.world_map = [[None for x in xrange(size)] for y in xrange(size)]
        self.plate_map = [[None for x in xrange(size)] for y in xrange(size)]
        self.temperature_map = [[None for x in xrange(size)] for y in xrange(size)]
        self.wind_map = [[None for x in xrange(size)] for y in xrange(size)]
        self.moisture_map = [[None for x in xrange(size)] for y in xrange(size)]
        self.empty = []
        self.image = im = Image.new('RGB', (self.size, self.size), 'white')

        for x in xrange(size):
            for y in xrange(size):
                self.empty.append((x,y))

        self.plate_symbols = [(255,248,220),(165,42,42),(36,24,130),(47,79,47),(139,0, 139),(66,111,66),(255,105,180),(255,69,0), (170,170,15)]
        self.centers = []
        self.plates = []
        self.fill_horizons = []

        self.start_plates()
        #self.fill_plates()
        self.flood_fill()
        self.find_edges()

    def show_map(self):
        pixels = self.image.load()

        for x in xrange(self.size):
            for y in xrange(self.size):
                if self.world_map[x][y] != None:
                    pixels[x,y] = self.world_map[x][y]
        self.image.show()

    def show_tempature_map(self):
        print 'creating temperature map image'
        pixels = self.image.load()

        for x in xrange(self.size):
            for y in xrange(self.size):
                val = int(self.temperature_map[x][y])
                pixels[x,y] = (val,val,val)

        for i, plate in enumerate(self.plates):
            for edge in plate.boundaries:
                x, y = edge
                if plate.is_oceanic:
                    pixels[x, y] = (0,0,100)
                else:
                    pixels[x, y] = (100, 0, 0)

        self.image.show()

    def start_plates(self, num_plates = 9):
        size = self.size
        for plate in xrange(num_plates):

            # random x, y point
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)

            # No perfectly overlappign plates
            while self.world_map[x][y] != None:
                x = random.randint(0, size - 1)
                y = random.randint(0, size - 1)

            self.world_map[x][y] = self.plate_symbols[plate]
            #self.plate_map[x][y] = plate # Comment me out if using flood fill
            self.centers.append((x,y))

            self.plates.append(Plate((x,y)))
            self.fill_horizons.append([])
            self.empty.remove((x,y))

    def flood_fill(self): # Make sure to comment out the line above
        q = Queue.Queue()
        for plate in xrange(len(self.plates)):
            q.put((self.plates[plate].center, plate))

        while not q.empty():
            coordinate, plate_num = q.get()
            x, y = coordinate
            if self.plate_map[x][y] == None:
                self.plates[plate_num].add_cell((x, y)) # Add square to plate
                self.plate_map[x][y] = plate_num # fill out plate map
                self.world_map[x][y] = self.plate_symbols[plate_num] #add color to world map

                if self.is_valid_and_empty(x-1, y) and random.randrange(2) == 0: q.put(((x-1, y), plate_num))
                if self.is_valid_and_empty(x+1, y) and random.randrange(2) == 0: q.put(((x+1, y), plate_num))
                if self.is_valid_and_empty(x, y-1) and random.randrange(2) == 0: q.put(((x, y-1), plate_num))
                if self.is_valid_and_empty(x, y+1) and random.randrange(2) == 0: q.put(((x, y+1), plate_num))
                if self.is_valid_and_empty(x-1, y+1) and random.randrange(2) == 0: q.put(((x-1, y+1), plate_num))
                if self.is_valid_and_empty(x+1, y+1) and random.randrange(2) == 0: q.put(((x+1, y+1), plate_num))
                if self.is_valid_and_empty(x-1, y-1) and random.randrange(2) == 0: q.put(((x-1, y-1), plate_num))
                if self.is_valid_and_empty(x+1, y-1) and random.randrange(2) == 0: q.put(((x+1, y-1), plate_num))

                q.task_done()

        # Scan for orphan cells and associate them with their most common neighbor
        for x in xrange(self.size):
            for y in xrange(self.size):
                q.put((x,y))

        while not q.empty():
            x, y = q.get()
            if self.plate_map[x][y] == None:
                neighbors = []
                if self.bounds(x-1,y): neighbors.append(self.plate_map[x-1][y])
                if self.bounds(x+1,y): neighbors.append(self.plate_map[x+1][y])
                if self.bounds(x+1,y+1): neighbors.append(self.plate_map[x+1][y+1])
                if self.bounds(x-1,y-1): neighbors.append(self.plate_map[x-1][y-1])
                if self.bounds(x+1,y-1): neighbors.append(self.plate_map[x+1][y-1])
                if self.bounds(x-1,y+1): neighbors.append(self.plate_map[x-1][y+1])
                if self.bounds(x,y+1): neighbors.append(self.plate_map[x][y+1])
                if self.bounds(x,y-1): neighbors.append(self.plate_map[x][y-1])

                neighbors = filter(lambda a: a != None, neighbors)

                if len(neighbors) > 0:
                    plate_num = max(set(neighbors), key=neighbors.count)
                    self.plate_map[x][y] = plate_num
                    self.world_map[x][y] = self.plate_symbols[plate_num] #add color to world map
                    q.task_done()
                else:
                    q.task_done()
                    q.put((x,y))



    def is_valid_and_empty(self, x, y):
        # Start by checking the bounds
        if self.bounds(x,y):
            return self.plate_map[x][y] == None
        return False

    def bounds(self, x, y):
        if x > 0 and x < self.size - 1 and y > 0 and y < self.size -1:
            return True
        return False

    def fill_plates(self):
        print 'creating plates'
        size = self.size
        count = 0
        while len(self.empty) != 0:
            # pick a plate
            plate = random.randint(0, len(self.plates) -1)
            if self.fill_horizons[plate] == []:
                x, y = random.choice(self.plates[plate].cells).coordinate
            else:
                x, y = random.choice(self.fill_horizons[plate])

            orig_x = x
            orig_y = y

            change = random.randint(1,2)
            sign = random.choice([-1,1])

            if change == 1: # change the x axis
                if x > 0 and x < size - 1:
                    x += sign
                else:
                    if sign == 1:
                        if x < size - 1:
                            x += sign
                        else:
                            x -= sign
                    else:
                        if x > 0:
                            x -= 1
                        else:
                            x += 1
            else:
                if y > 0 and y < size - 1:
                    y += sign
                else:
                    if sign == 1:
                        if y < size - 1:
                            y += sign
                        else:
                            y -= sign
                    else:
                        if y > 0:
                            y -= 1
                        else:
                            y += 1

            # Now x,y is our coordinate. If it's not an empty square get out of here
            if (x, y) not in self.empty:
                continue

            self.plates[plate].add_cell((x,y))
            self.plate_map[x][y] = plate
            self.fill_horizons.append((x,y))

            if len(self.fill_horizons[plate]) != 0:
                # remove the point we came from from the horizon
                self.fill_horizons.remove((orig_x, orig_y))

            self.world_map[x][y] = self.plate_symbols[plate]
            self.empty.remove((x,y))

    def find_edges(self):
        print 'finding edges'
        for plate in xrange(len(self.plate_symbols)):
            for cell in self.plates[plate].cells:
                x, y = cell.coordinate
                neighbors = self.valid_neighbors(cell.coordinate)
                for n in neighbors:
                    n_x, n_y = n
                    if self.plate_map[x][y] != self.plate_map[n_x][n_y]:
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

                plate = self.plate_map[x][y]
                if self.plates[plate].is_oceanic:
                   basic_temp = helper.clamp(basic_temp - constants.OCEAN_TEMP, 0, 255)
                self.temperature_map[x][y] = basic_temp

    def normalize_temperatures(self):
        # normalize temp values:
        sum = 0.0
        for x in xrange(self.size):
            for y in xrange(self.size):
                sum += self.temperature_map[x][y]
        avg = sum / (self.size**2)

        dif_sum = 0.0
        for x in xrange(self.size):
            for y in xrange(self.size):
                dif_sum += (self.temperature_map[x][y] - sum)**2
        varience = dif_sum / (self.size**2)
        std_deviation = math.sqrt(varience)

        #apply std score
        for x in xrange(self.size):
            for y in xrange(self.size):
                print (self.temperature_map[x][y] - avg)/std_deviation
                self.temperature_map[x][y] = (self.temperature_map[x][y] - avg)/std_deviation

    def populate_wind(self):
        for x in xrange(self.size):
            for y in xrange(self.size):
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

                spin_direction = 180 if y - (self.size/2) > 0 else 0
                spin_v = Vector(abs((y - (self.size/2))) * constants.WINDSPEED, spin_direction)

                self.wind_map[x][y] = sum_vector.add(spin_v)

    def populate_moisture(self):
        None

    def heat_vector(self, cell, neighbor, direction):
        cell_x, cell_y = cell
        n_x, n_y = neighbor
        c = self.temperature_map[cell_x][cell_x]
        n = self.temperature_map[n_x][n_y]

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
            if self.temperature_map[n_x][n_y] != None:
                combined_heat += self.temperature_map[n_x][n_y]
                num_neighbors += 1
        return combined_heat, num_neighbors

def main():
    constants.init()
    plates = Plates()
    plates.show_map()
    plates.populate_temperature()
    plates.populate_wind()
    plates.show_tempature_map()

if __name__=='__main__':
    import time
    start_time = time.clock()
    main()
    print time.clock() - start_time, "seconds"