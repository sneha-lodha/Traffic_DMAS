import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector

from background import Background
from car import Car
from controller import Controller
from trafficlight import Traffic_light


class Grid(Model):
    """A model of a four way intersection. Cars can depart from every
    direction, and can travel in any of the three other directions.
    The flow of traffic coming from any of the four directions can be
    controlled through the use of the sliders. Each of the lanes features a
    traffic light which periodically turns green. The user determines whether
    the fixed time, flow based, or demand based system is used.
    """

    def __init__(self, east_flow, west_flow, north_flow, south_flow, system):
        """The Grid class deals with the actual model of the whole simulation
        and add all the agents to the grid and initializes the model.

        We use MultiGrid, which means that multiple agents can be added to the
        same cell.

        Four flow parameters are passed to initalize the model. These represent
        flow of the cars from the 4 different directions in the simulation.
        """
        self.grid = MultiGrid(25, 25, False)
        self.schedule = BaseScheduler(self)
        self.running = True
        self.id = 0
        self.traffic_lights = []
        self.flows = [east_flow, west_flow, north_flow, south_flow]
        self.car_counter = 0
        self.wait_times = []
        self.average_wait_time = 0
        self.dctt = DataCollector(model_reporters={
            "Avg wait time": lambda model: model.average_wait_time})
        self.dccc = DataCollector(model_reporters={
            "Car count": lambda model: model.car_counter})
        self.system = system

        # Add all the different agents to the blocks in the model
        self.add_roads()
        self.add_barriers()
        self.finish_background()
        self.add_traffic_lights()
        self.add_controller()

    def count_cars(self):
        """ Function to count the number of cars that have cleared the model.
        They are counted when they have successfully crossed the intersection
        and left the screen.
        """
        self.car_counter += \
            len(self.grid.get_cell_list_contents((0, 14))) + \
            len(self.grid.get_cell_list_contents((10, 0))) + \
            len(self.grid.get_cell_list_contents((24, 10))) + \
            len(self.grid.get_cell_list_contents((14, 24))) - 4

        print("COUNT", self.car_counter)
        return self.car_counter

    def calculate_average_wait_time(self):
        """Calculate the average waiting time of all the cars that are
        currently and were previously on the grid
        """
        all_agents = []
        all_agents += self.grid.get_cell_list_contents((0, 14))
        all_agents += self.grid.get_cell_list_contents((10, 0))
        all_agents += self.grid.get_cell_list_contents((24, 10))
        all_agents += self.grid.get_cell_list_contents((14, 24))
        for agent in all_agents:
            if (agent.type == "car"):
                self.wait_times.append(agent.wait_time)
        if len(self.wait_times) != 0:
            self.average_wait_time = sum(self.wait_times)/len(self.wait_times)
            print("Average travel time of cars is:", self.average_wait_time)
        else:
            print("No cars have passed yet")
            return 0

    def add_controller(self):
        """Add the controller of the demand based system to the grid"""
        controller = Controller(self.id, self)
        self.schedule.add(controller)
        self.grid.place_agent(controller, (0, 0))   # makes it easier to find
        self.id += 1

    def add_background_agent(self, color, x, y):
        """Function that given a color and a position (x, y) fills
        that position with the background color.
        """
        self.grid.place_agent(Background(self.id, self, color), (x, y))
        self.id += 1

    def add_road(self, direction, position, begin, end):
        """Function that places a background agent with the color gray to
        mimic a road. This take direction as a prameter to determine which
        direction the road takes.
        """
        for i in range(begin, end):
            if direction == 'east':
                if self.grid.is_cell_empty([i, position]):
                    self.add_background_agent('grey', i, position)
            if direction == 'north':
                if self.grid.is_cell_empty([position, i]):
                    self.add_background_agent('grey', position, i)

    def add_roads(self):
        """Function that adds all the different roads to the simualation"""
        self.add_road('east', 9, 0, 10)
        self.add_road('east', 10, 0, self.grid.width)
        self.add_road('east', 11, 0, 15)

        self.add_road('east', 13, 10, self.grid.width)
        self.add_road('east', 14, 0, self.grid.width)
        self.add_road('east', 15, 15, self.grid.width)

        self.add_road('north', 13, 0, 15)
        self.add_road('north', 14, 0, self.grid.height)
        self.add_road('north', 15, 0, 10)

        self.add_road('north', 9, 15, self.grid.height)
        self.add_road('north', 10, 0, self.grid.height)
        self.add_road('north', 11, 10, self.grid.height)

    def add_barrier(self, direction, position, length):
        """Add a single barrier to the grid"""
        for i in range(0, length):
            if direction == 'east':
                if self.grid.is_cell_empty([i, position]):
                    self.add_background_agent('darkslategrey', i, position)
            if direction == 'north':
                if self.grid.is_cell_empty([position, i]):
                    self.add_background_agent('darkslategrey', position, i)

    def add_barriers(self):
        """Calls add_barrier() to add all the barriers to the grid"""
        self.add_barrier('east', 11, self.grid.width)
        self.add_barrier('east', 12, self.grid.width)
        self.add_barrier('east', 13, self.grid.width)

        self.add_barrier('north', 11, self.grid.height)
        self.add_barrier('north', 12, self.grid.height)
        self.add_barrier('north', 13, self.grid.height)

    def finish_background(self):
        """ Adds a large background agent with the same size of the grid """
        self.add_background_agent('green', 12, 12)

    def add_traffic_light(self, x, y, direction, turn=''):
        """Adds a traffic light to the grid and the scheduler.

        (x, y) are the coordinates of the light and direction is the direction
        of flow that the traffic light controls.
        """
        traffic_light = Traffic_light(self.id, self, direction, turn)
        self.grid.place_agent(traffic_light, (x, y))
        self.schedule.add(traffic_light)
        self.id += 1
        self.traffic_lights.append(traffic_light)

    def add_traffic_lights(self):
        """Add all the traffic lights to the grid"""
        self.add_traffic_light(9, 9, 'east', 'right')
        self.add_traffic_light(9, 10, 'east')
        self.add_traffic_light(9, 11, 'east', 'left')

        self.add_traffic_light(15, 13, 'west', 'left')
        self.add_traffic_light(15, 14, 'west')
        self.add_traffic_light(15, 15, 'west', 'right')

        self.add_traffic_light(13, 9, 'north', 'left')
        self.add_traffic_light(14, 9, 'north')
        self.add_traffic_light(15, 9, 'north', 'right')

        self.add_traffic_light(9, 15, 'south', 'right')
        self.add_traffic_light(10, 15, 'south')
        self.add_traffic_light(11, 15, 'south', 'left')

    def add_car(self, direction, x, y, flow):
        """Function to add a car to grid at position (x, y) going in the
        given direction.

        The chance a car is added is based on the value of the flow.
        """
        rand = random.randint(1, 100)
        if flow > rand:
            cell = list(self.grid.iter_cell_list_contents((x, y)))
            for agent in cell:
                if (agent.type == 'car'):
                    return
            car = Car(self.id, self, direction)     # create new car
            self.grid.place_agent(car, (x, y))
            self.schedule.add(car)
            self.id += 1

    def calculate_on_time(self, flow):
        """Function that given the value of the flow in a certain direction,
        determines how long the light should stay green.

        If the flow is higher than 50, the light stays green for 20 time
        steps, otherwise for only 10 time steps.
        """
        if flow < 50:
            time = 10
        else:
            time = 20
        return time

    def calculate_timer(self):
        """Based on the flow of the cars from different directions,
        calculates the times at which the lights should switch colors.

        Always a pause of 8 seconds between green lights to avoid crashes.
        """
        on_times = []
        # Calculates on times for each direction based on flow.
        for flow in self.flows:
            on_times.append(self.calculate_on_time(flow))

        # Adding 8 is the pause of 8 seconds between different green lights.
        first = 8
        second = first + on_times[0]
        third = second + 8
        fourth = third + on_times[1]
        fifth = fourth + 8
        sixth = fifth + on_times[2]
        seventh = sixth + 8
        eighth = seventh + on_times[3]

        return [first, second, third, fourth, fifth, sixth, seventh, eighth]

    def step(self):
        """Step function that is automatically called at each time step of
        the model.

        Attempt to add cars in all directions based on the flow value.
        Also count the amount of cars passed and update the average
        wait time and the car count
        """
        self.schedule.step()
        self.add_car('east', 0, 9, self.flows[0])
        self.add_car('east', 0, 10, self.flows[0])
        self.add_car('east', 0, 11, self.flows[0])

        self.add_car('west', 24, 13, self.flows[1])
        self.add_car('west', 24, 14, self.flows[1])
        self.add_car('west', 24, 15, self.flows[1])

        self.add_car('north', 13, 0, self.flows[2])
        self.add_car('north', 14, 0, self.flows[2])
        self.add_car('north', 15, 0, self.flows[2])

        self.add_car('south', 9, 24, self.flows[3])
        self.add_car('south', 10, 24, self.flows[3])
        self.add_car('south', 11, 24, self.flows[3])
        self.count_cars()
        self.calculate_average_wait_time()
        self.dctt.collect(self)
        self.dccc.collect(self)
