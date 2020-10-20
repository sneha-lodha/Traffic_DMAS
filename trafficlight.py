import random

from mesa import *


class Traffic_light(Agent):
    """Class that is responsible for the functionality of the traffic
    lights.

    Each traffic light has a direction and turn and it has a color so
    it can change from red to green and vice versa. If traffic lights
    are red, cars are not allowed to pass, whereas if they are green
    cars are allowed to pass.

    In this class we test different methods on determining when the lights
    change color.
    """

    def __init__(self, id, model, direction, turn='no turn'):
        super().__init__(id, model)
        self.type = 'light'
        self.color = 'red'
        self.time = 0
        self.direction = direction
        self.turn = turn
        self.demand = 0
        self.waiting_time = 0
        self.car_waiting = False

    def timer1(self):
        """First timer that changes light in a brute force way, where
        the times are already predetermined. The first naive approach
        to the traffic light logic.

        The time variable is incremented and reset once it reaches 32 so
        this runs in a loop fashion.
        """
        if self.time == 5:
            if self.direction == 'north':
                self.setColor('red')
        if self.time == 8:
            if self.direction == 'east':
                self.setColor('green')
        if self.time == 13:
            if self.direction == 'east':
                self.setColor('red')
        if self.time == 16:
            if self.direction == 'south':
                self.setColor('green')
        if self.time == 21:
            if self.direction == 'south':
                self.setColor('red')
        if self.time == 24:
            if self.direction == 'west':
                self.setColor('green')
        if self.time == 29:
            if self.direction == 'west':
                self.setColor('red')
        if self.time == 32:
            if self.direction == 'north':
                self.setColor('green')
            self.time = 0
        self.time += 1

    def timer2(self, times):
        """Timer that is semi-brute force.

        This timer when called with the calculate_timer() in the grid.py
        sets the correct intervals based on the flows of the traffic from
        the different directions. Very similar to timer1() but times are
        pre-calculated.
        """
        if self.time == times[0]:
            if self.direction == 'east':
                self.setColor('green')
        if self.time == times[1]:
            if self.direction == 'east':
                self.setColor('red')
        if self.time == times[2]:
            if self.direction == 'west':
                self.setColor('green')
        if self.time == times[3]:
            if self.direction == 'west':
                self.setColor('red')
        if self.time == times[4]:
            if self.direction == 'north':
                self.setColor('green')
        if self.time == times[5]:
            if self.direction == 'north':
                self.setColor('red')
        if self.time == times[6]:
            if self.direction == 'south':
                self.setColor('green')
        if self.time == times[7]:
            if self.direction == 'south':
                self.setColor('red')
            self.time = 0
        self.time += 1


    def timer3(self):
        """Check with the controller whether the light should be green or red.
        The 7 second pause assurres there are no collisions between cars"""
        cell = list(self.model.grid.iter_cell_list_contents((0, 0)))
        for agent in cell:
            if (agent.type == 'controller'):
            	controller = agent
        if self.direction == controller.green_lights and controller.time > 7:
            self.setColor('green')
            self.waiting_time = 0
        else: 
        	self.setColor('red')

    def calculate_demand(self):
        """Calculate the demand of the traffic light. The demand is calculated
        as the amount of cars that are in the 10 cells in front of the light"""
        self.demand = 0
        self.car_waiting = False
        for i in range(0,10):
            if self.direction == 'east':
                if self.car_present(self.pos[0] - i, self.pos[1]):
                    self.update_variables(i)
            if self.direction == 'west':
                if self.car_present(self.pos[0] + i, self.pos[1]):
                    self.update_variables(i)
            if self.direction == 'south':
                if self.car_present(self.pos[0], self.pos[1] + i):
                    self.update_variables(i)
            if self.direction == 'north':
                if self.car_present(self.pos[0], self.pos[1] - i):
                    self.update_variables(i)

    def car_present(self, x, y):
        """Return whether there is a car 
        at the location of the traffic light"""
        cell = list(self.model.grid.iter_cell_list_contents((x, y)))
        for agent in cell:
            if (agent.type == 'car'):
                return True
        return False

    def update_variables(self, i):
        self.demand += 1
        if i == 0:
            self.car_waiting = True
            self.waiting_time += 1


    def setColor(self, color):
        """Set the color od the light, either green or red."""
        self.color = color

    def getColor(self):
        """Get the current color of the light."""
        return self.color

    def getType(self):
        """Returns light as the type of the agent."""
        return self.type

    def getDirection(self):
        """Returns the direction of the light."""
        return self.direction

    def get_car_waiting(self):
        return self.car_waiting

    def get_direction(self):
        return self.direction

    def get_demand(self):
        return self.demand

    def get_waiting_time(self):
        return self.waiting_time

    def step(self):
        """Step function of the light called every time step.

        Call either with timer1() or timer2() to see how the lights in the model
        change colors.
        """
        # times = self.model.calculate_timer()
        # self.timer2(times)
        self.calculate_demand()
        self.timer3()
