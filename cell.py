__author__ = 'fopitz'


class Cell():
    def __init__(self, coordinate, elevation):
        self.coordinate = coordinate
        self.elevation = elevation
        self.temperature = 0
        self.windspeed = None

    def set_temperature(self, temperature):
        self.temperature = temperature

    def set_windspeed(self, windspeed):
        self.windspeed = windspeed