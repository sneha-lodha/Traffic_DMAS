from mesa import *

class Controller(Agent):

    def __init__(self, id, model):
        super().__init__(id, model)		# required, part of mesa
        self.type = 'controller'
        self.green_lights = 'east'
        self.time = 0
        self.delay_limit = 60


    def determine_light(self):
        """Determine which combination of lights has the highest demand.
        The time variable assures 7 second interval between two green lights"""
        self.time += 1
        demands = self.combine_demands()
        highest_demand = max(demands, key=demands.get)
        self.check_delay_limit()
        if not self.car_waiting_long():
            if demands[self.green_lights] < demands[highest_demand] - 6 :
                if not self.car_waiting():
                    self.green_lights = highest_demand
                    self.time = 0

    def car_waiting(self):
        for light in self.model.traffic_lights:
            if light.get_direction() == self.green_lights:
                if light.get_car_waiting() == False:
                    return False
        return True
        

    def check_delay_limit(self):
        if self.delay_limit > 60:
            for light in self.model.traffic_lights:
                if light.get_waiting_time() > self.delay_limit - 16:
                    return
            self.delay_limit -= 16

    def car_waiting_long(self):
        for light in self.model.traffic_lights:
            if light.get_waiting_time() > self.delay_limit:
                self.green_lights = light.get_direction()
                if self.time > 8:
                    self.time = 0
                    self.delay_limit += 16
                return True
        return False

    def combine_demands(self):
        """Combine the demands of the individual lights 
        in the different groups of lights"""
        demands = {'east': 0, 'west': 0, 'north': 0, 'south': 0}
        for light in self.model.traffic_lights:
            demands[light.get_direction()] += light.get_demand()
        return demands



    def getType(self):
        """Get the type of the agent"""
        return self.type

    def step(self):
        """Called every step for every individual car"""
        self.determine_light()
