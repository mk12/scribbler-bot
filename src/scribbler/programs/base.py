# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements common functionality for Scribbler programs."""

import myro

BEEP_LEN = 0.5
BEEP_FREQ = 2000

SPEEDS = [x/10.0 for x in range(1, 11)]
DEFAULT_SPEED_INDEX = 4

class BaseProgram(object):
    """A base program that handles some of the details that communication with
    the server involves."""

    def __init__(self):
        """Creates a new base program."""
        self.speed_ind = DEFAULT_SPEED_INDEX

    @property
    def speed(self):
        """."""
        return SPEEDS[self.speed_ind]

    def accel(self, dv):
        """Changes the robot's speed by the given delta."""
        self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed + dv))

    # Subclasses should override the following methods (and call super).
    # __call__ and loop must return a status.

    def __call__(self, command):
        """Performs an action according to the command passed down from the
        controller, and returns a status message."""
        if command == 'speed:inc':
            if self.speed_ind == len(SPEEDS) - 1:
                return "already at max speed"
            self.speed_ind += 1
            return "inc'd speed to {}".format(self.speed)
        if command == 'speed:dec':
            if self.speed == 0:
                return "already at min speed"
            self.speed_ind -= 1
            return "dec'd speed to {}".format(self.speed)
        if command == 'other:beep':
            myro.beep(BEEP_LEN, BEEP_FREQ)
        if command == 'other:info':
            return myro.getInfo()
        return None

    def start(self):
        """Called when the controller is started."""
        pass

    def stop(self):
        """Called when the controller is stopped."""
        myro.stop()

    def reset(self):
        """Resets the program to its initial state."""
        pass

    def loop(self):
        """The main loop of the program."""
        return "long-polling update"
