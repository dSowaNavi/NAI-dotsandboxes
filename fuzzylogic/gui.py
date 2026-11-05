import tkinter as tk
from tkinter import ttk
import random
from ac_manager import AcManager



class AcGui:
    """
    This class renders the UI and simulates an environment for the ac to work in.

    The app window is generated using the tkinter ttk package that displays the current state of the ac unit and its environment.
    Every update tick it adjusts the room temperature with a random value and with the output from the ac_manager.
    the update tick depends on update_interval.

    The UI also allows for manually changing the current temperature and desired temperature as well as dumping the liquid container.

    Class variables:
    root (tk.Tk) : main tkinter application window
    ac_simulator (AcManager): an instance of AcManager. It is used for fuzzy calculations and managing the ac parameters
    cooling_power (float): Currently calculated cooling power.
    random_variable (float): Random temperature change applied during each tick
    update_interval (int): Time between ticks

    """

    def __init__(self, root, ac_simulator):
        self.root = root
        self.ac_simulator = ac_simulator
        self.cooling_power = 0
        self.random_variable = 0
        # define the title, size and property of the tkinter window
        self.root.title("PJATK AC simulator ")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        # time between ticks
        self.update_interval = 2000

        self.create_widgets()

        self.update_simulation()

        # render a tkinter window
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(main_frame, text="Ac simulator, creators: s24589 and s31893", font=("Arial", 18, "bold"))
        title.pack(pady=15)

        # create labels for each of the control variables
        self.temperature_label = ttk.Label(main_frame, text="Current temperature: ", font=("Arial", 18))
        self.temperature_label.pack(pady=10)

        self.desired_label = ttk.Label(main_frame, text="Desired temperature: ", font=("Arial", 18))
        self.desired_label.pack(pady=10)

        self.cooling_power_label = ttk.Label(main_frame, text="Current power: ", font=("Arial", 18))
        self.cooling_power_label.pack(pady=10)

        self.liquid_capacity = ttk.Label(main_frame, text="Capacity: ", font=("Arial", 18))
        self.liquid_capacity.pack(pady=10)

        self.rand_var = ttk.Label(main_frame, text="Random Variable: ", font=("Arial", 18))
        self.rand_var.pack(pady=10)


        ttk.Separator(main_frame).pack(fill="x", pady=15)

        # defines an input field for current temperature
        self.temperature_entry = ttk.Entry(main_frame, width=15)
        self.temperature_entry.pack(pady=5)

        # button invoking function responsible for changing current temperature
        ttk.Button(
            main_frame,
            text="Set Current Temperature",
            command=self.change_temperature
        ).pack(pady=5)

        # defines an input field for desired temperature
        self.desired_entry = ttk.Entry(main_frame, width=15)
        self.desired_entry.pack(pady=5)

        # button invoking function responsible for changing desired temperature
        ttk.Button(
            main_frame,
            text="Set Desired Temperature",
            command=self.change_desired
        ).pack(pady=5)

        # button invoking the function responsible for resetting the container capacity
        ttk.Button(
            main_frame,
            text="Empty Container Capacity",
            command=self.empty_capacity
        ).pack(pady=10)


    def update_simulation(self):

        """
        Calculates new cooling power and adjusts current temperature based on the cooling power and random variable.
        Once the update is done it schedules the next update. This happens every tick, based on update_interval.
        1. Calculate cooling power using fuzzy controller from ac_simulator
        2. reduce the current temperature using the calculated cooling power
        3. generate a random value to simulate outside weather. it is then applied to current temperature.
        4. Increase the container capacity based on the cooling power
        5. Re-render the UI
        """

        # use ac_manager to generate our simulated cooling power and use it to affect current temperature in the room
        self.cooling_power = self.ac_simulator.calculate_output()


        self.ac_simulator.adjust_current_temperature(-self.cooling_power)

        # change the current temperature of the room using a random variable to simulate weather changes
        self.random_variable = random.uniform(-2, 10)
        self.ac_simulator.adjust_current_temperature(self.random_variable)

        # simulate the liquid tank in the ac gradually filling up
        self.ac_simulator.adjust_capacity(self.cooling_power * 0.5)

        self.refresh_display ()

        # call this function again after set amount of time
        self.root.after( self.update_interval, self.update_simulation)

    def refresh_display(self):

        """
        Updates all labels with the current simulation values.

        """

        self.temperature_label.config(
            text=f"Current Temperature: {self.ac_simulator.current_temperature:.2f}°C"
        )

        self.desired_label.config(
            text=f"Desired Temperature: {self.ac_simulator.desired_temperature:.2f}°C"
        )

        self.cooling_power_label.config(
            text=f"Cooling power: {self.cooling_power:.2f}"
        )

        self.rand_var.config(
            text=f"Random Variable: {self.random_variable:.2f}°C"
        )

        self.liquid_capacity.config(
            text=f"Capacity: {self.ac_simulator.get_capacity():.2f}%"
        )



    def change_temperature(self):
        """
        change current temperature using user input.
        New value is taken from temperature_entry input field, converts it into a float and passes t to the AcManager instance.
        After the change is made the UI is Rerendered
        """
        new_temperature = float(self.temperature_entry.get())
        self.ac_simulator.set_current_temperature(new_temperature)
        self.refresh_display()

    def change_desired(self):
        """
        change desired temperature using user input.
        New value is taken from desired_entry input field, converts it into a float and passes t to the AcManager instance.
        After the change is made the UI is Rerendered
        """
        new_temperature = float(self.desired_entry.get())
        self.ac_simulator.set_desired_temperature(new_temperature)
        self.refresh_display()

    # change capacity to 0
    def empty_capacity(self):
        """
        Empty the air conditioner's container.

        Calls the AcManager dump_capacity() method, which resets
        container capacity to zero.
        """
        self.ac_simulator.dump_capacity()
        self.refresh_display()















