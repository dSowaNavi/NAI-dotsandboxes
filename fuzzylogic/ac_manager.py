import skfuzzy
from skfuzzy import control
import numpy as np



class AcManager:
    """
    This class handles the calculations for an AC. It contains all information about its environment and calculates appropriate cooling power using fuzzy logic

    The cooling power is calculated based on variables desired_temperature, current_temperature and container_capacity.
    Fuzzy logic is handles using skfuzzy library and numpy.

    Class variables:
    desired_temperature (float): the desired temperature of the room
    current_temperature (float): the current temperature of the room
    container_capacity (float): the capacity of the container with the condensate
    cooling_power (float): the cooling power of the ac unit

    fuzzy_current_temperature: skfuzzy,fuzzy input ranging from 10 to 40 C representing the current temperature in the room
    fuzzy_desired_temperature: skfuzzy,fuzzy input ranging from 13 to 35 C representing the desired temperature in the room
    fuzzy_container_capacity: skfuzzy,fuzzy input representing container capacity from 0 to 100 %.
    fuzzy_cooling_power: skfuzzy Fuzzy output representing cooling power from 0 to 10.

    rules (list): list containing all rules for fuzzy logic used by the controller
    ac_controller: skfuzzy control system.
    ac_simulator: skfuzzy control system simulation instance.

    """

    def __init__(self, desired_temperature, current_temperature, container_capacity):
        self.desired_temperature = desired_temperature
        self.current_temperature = current_temperature
        self.container_capacity = container_capacity
        self.cooling_power = 0

        # define three fuzzy inputs and one output
        self.fuzzy_current_temperature = control.Antecedent(np.arange(10, 41, 1), 'current_temp')
        self.fuzzy_desired_temperature = control.Antecedent(np.arange(13, 36, 1), 'desired_temp')
        self.fuzzy_container_capacity = control.Antecedent(np.arange(0, 101, 1), 'container_capacity')
        self.fuzzy_cooling_power = control.Consequent(np.arange(0, 11, 1), 'cooling_power')

        # define fuzzy sets for inputs current temperature, desired temperature, and container capacity
        self.fuzzy_current_temperature['cold'] = skfuzzy.trimf(self.fuzzy_current_temperature.universe, [10,10,22])
        self.fuzzy_current_temperature['comfortable'] = skfuzzy.trimf(self.fuzzy_current_temperature.universe, [20, 25, 35])
        self.fuzzy_current_temperature['hot'] = skfuzzy.trimf(self.fuzzy_current_temperature.universe, [30, 40, 40])

        self.fuzzy_desired_temperature['cold'] = skfuzzy.trimf(self.fuzzy_desired_temperature.universe, [13,13,20])
        self.fuzzy_desired_temperature['comfortable'] = skfuzzy.trimf(self.fuzzy_desired_temperature.universe, [17, 20, 25])
        self.fuzzy_desired_temperature['hot'] = skfuzzy.trimf(self.fuzzy_desired_temperature.universe, [23, 35, 35])

        self.fuzzy_container_capacity['low'] = skfuzzy.trimf(self.fuzzy_container_capacity.universe, [0, 0 , 30])
        self.fuzzy_container_capacity['medium'] = skfuzzy.trimf(self.fuzzy_container_capacity.universe, [20, 40, 65])
        self.fuzzy_container_capacity['high'] = skfuzzy.trimf(self.fuzzy_container_capacity.universe, [50, 70, 90])
        self.fuzzy_container_capacity['critical'] = skfuzzy.trimf(self.fuzzy_container_capacity.universe, [85, 100, 100])

        # define fuzzy set for the output
        self.fuzzy_cooling_power['low'] = skfuzzy.trimf(self.fuzzy_cooling_power.universe, [0, 2 , 4])
        self.fuzzy_cooling_power['medium'] = skfuzzy.trimf(self.fuzzy_cooling_power.universe, [3, 5, 7])
        self.fuzzy_cooling_power['high'] = skfuzzy.trimf(self.fuzzy_cooling_power.universe, [5, 7, 9])
        self.fuzzy_cooling_power['max'] = skfuzzy.trimf(self.fuzzy_cooling_power.universe, [8, 10, 10])

        self.rules = []

        # generate fuzzy rules and initiate the controller and simulator
        self.generate_rules()
        self.create_fuzzy_system()


    """
    generate all fuzzy rules based on a dict of states in which the room can be. These rules are then used for determining cooling power.
    To simplify the process of modifying the rules they are generated automatically rather then written manually.
    The cooling power is calculated based on current and desired temperature classifications, it is then reduces depending on current container capacity.
    """

    def generate_rules(self):

        # here the current room temperature is compared to the desired temperature and the cooling power is the result
        temperature_rules = {
            ('cold', 'cold') : 'low',
            ('cold', 'comfortable') : 'low',
            ('cold', 'hot') : 'low',

            ('comfortable', 'cold') : 'high',
            ('comfortable', 'comfortable') : 'low',
            ('comfortable', 'hot') : 'low',

            ('hot', 'cold') : 'max',
            ('hot', 'comfortable') : 'high',
            ('hot', 'hot') : 'low',
        }

        # all possible power levels sorted by strength
        power_levels = [
            'low',
            'medium',
            'high',
            'max'
        ]

        # the fuller the tank, the slower the machine will run. here we define how severe the reduction is
        capacity_reduction = {
            'low': 0,
            'medium': 1,
            'high': 2,
            'critical': 4
        }

        # iterate over the dictonary of temperature relations and determine power reduction
        for (current, desired), base_power in temperature_rules.items():
            for capacity, reduction in capacity_reduction.items():
                # determine what the power is after reduction
                base_power_index = power_levels.index(base_power)
                new_power_index = max(0, base_power_index - reduction)
                new_power = power_levels[new_power_index]

                # create a new fuzy rule for each combination of current and desired temperatures, capacity and output power with applied reduction
                rule = control.Rule(
                    self.fuzzy_current_temperature[current]  &
                    self.fuzzy_desired_temperature[desired] &
                    self.fuzzy_container_capacity[capacity] ,
                    self.fuzzy_cooling_power[new_power]
                )

                self.rules.append(rule)

    # define a skfuzzy controller and simulator using previously generated rules. The rules need to be first generated in order to create the controller.
    def create_fuzzy_system(self):
        self.ac_controller = control.ControlSystem(self.rules)
        self.ac_simulator = control.ControlSystemSimulation(self.ac_controller, cache=False)

    # calculate the cooling power using built in skfuzzy simulator and interface using provided values
    def calculate_output(self):

        # if desired temperature was reached or the capacity was exceeded shut down the unit.
        if self.current_temperature <= self.desired_temperature or self.container_capacity >= 100:
            self.cooling_power = 0
            return 0

        self.ac_simulator.input['current_temp'] = self.current_temperature
        self.ac_simulator.input['desired_temp'] = self.desired_temperature
        self.ac_simulator.input['container_capacity'] = self.container_capacity

        # execute the simulation and defuzzify results
        self.ac_simulator.compute()
        self.cooling_power = self.ac_simulator.output['cooling_power']

        return self.cooling_power


    """
    define setters and getters for adjusting the simulation
    The resulting temperature is restricted to the supported fuzzy input range of 13-35 degrees Celsius for desired temperature. and range of 10-40 Celsius for current temperature.
    """

    def adjust_desired_temperature(self, value):
        self.desired_temperature += value
        self.current_temperature = max(13, min(36, self.desired_temperature))

    def adjust_current_temperature(self, value):
        self.current_temperature += value
        self.current_temperature = max(10, min(40, self.current_temperature))

    def set_current_temperature(self, value):
        self.current_temperature = max(10, min(40, value))

    def set_desired_temperature(self, value):
        self.desired_temperature = max(10, min(40, value))

    def get_capacity(self):
        return self.container_capacity

    def adjust_capacity(self, value):
        if self.container_capacity < 100:
            self.container_capacity += value

    def dump_capacity(self):
        self.container_capacity = 0