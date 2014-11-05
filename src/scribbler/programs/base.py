# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements common functionality for Scribbler programs."""

import math
from time import time


# Short codes for the parameters of the program.
PARAM_CODES = {
    'bl': 'beep_len',
    'bf': 'beep_freq',
    's': 'speed',
    'dtt': 'dist_to_time',
    'att': 'angle_to_time'
}


# Default values for the parameters of the program.
PARAM_DEFAULTS = {
    'beep_len': 0.5, # s
    'beep_freq': 2000, # Hz
    'speed': 0.4, # from 0.0 to 1.0
    'dist_to_time': 0.07, # cm/s
    'angle_to_time': 0.009 # rad/s
}


# Prefix used in commands that change the value of a parameter.
PARAM_PREFIX = 'set:'


class BaseProgram(object):

    """Implements the general aspects of robot programs and basic server
    communcation. Also manages the parameter dictionary."""

    def __init__(self):
        """Creates a new base program."""
        self.params = PARAM_DEFAULTS.copy()
        self.codes = PARAM_CODES.copy()

    def add_params(self, defaults, codes):
        """Adds parameters to the program given their default values and their
        short codes, which must be dictionaries similar to PARAM_CODES and
        PARAM_DEFAULTS (defined above)."""
        self.params.update(defaults)
        self.codes.update(codes)

    @property
    def speed(self):
        """Returns the nominal speed of the robot."""
        return self.params['speed']

    def dist_to_time(self, dist):
        """Returns how long the robot should drive at its current speed in order
        to cover `dist` centimetres."""
        return self.params['dist_to_time'] * dist / self.speed

    def angle_to_time(self, angle):
        """Returns how long the robot should rotate at its current speed in
        order to rotate by `angle` degrees."""
        return self.params['angle_to_time'] * angle / self.speed

    def radians_to_time(self, theta):
        """Like `angle_to_time`, but the angle is in radians."""
        return self.angle_to_time(180 * theta / math.pi)

    def time_to_dist(self, time):
        """The inverse of `dist_to_time`."""
        return self.speed * time / self.params['dist_to_time']

    # Subclasses should override the following methods (and call super).
    # `__call__` must return a status, and `loop` should sometimes.

    def __call__(self, command):
        """Performs an action according to the command passed down from the
        controller, and returns a status message."""
        if command == 'other:beep':
            myro.beep(self.params['beep_len'], self.params['beep_freq'])
            return "successful beep"
        if command == 'other:info':
            return "battery: " + str(myro.getBattery())
        if command.startswith(PARAM_PREFIX):
            code, value = command[len(PARAM_PREFIX):].split('=')
            if not code in self.codes:
                return "invalid code: " + code
            name = self.codes[code]
            # Return the value of the parameter.
            if value == "" or value == "?":
                return name + " = " + str(self.params[name])
            try:
                n = float(value)
            except ValueError:
                return "NaN: " + value
            # Set the parameter to the new value.
            self.params[name] = n
            return name + " = " + value
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
        pass


class ModeProgram(BaseProgram):

    """A program that operates in one mode per distinct motion."""

    def __init__(self, initial_mode):
        """Creates a new ModeProgram it its default state."""
        BaseProgram.__init__(self)
        self.initial_mode = initial_mode
        self.reset()

    def reset(self):
        """Stops and resets the program to the first mode."""
        BaseProgram.reset(self)
        self.mode = self.initial_mode
        self.start_time = 0
        self.pause_time = 0

    def stop(self):
        """Pauses and records the current time."""
        BaseProgram.stop(self)
        self.pause_time = time()

    def start(self):
        """Resumes the program and fixes the timer so that the time while the
        program was paused doesn't count towards the mode's time."""
        BaseProgram.start(self)
        self.start_time += time() - self.pause_time
        self.move()

    def goto_mode(self, mode):
        """Stops the robot and switches to the given mode. Resets the timer and
        starts the new mode immediately."""
        myro.stop()
        self.end_mode()
        self.mode = mode
        self.start_time = time()
        self.begin_mode()
        self.move()

    def mode_time(self):
        """Returns the time that has elapsed since the mode begun."""
        return time() - self.start_time

    def has_elapsed(self, t):
        """Returns true if `t` seconds have elapsed sicne the current mode begun
        and false otherwise."""
        return self.mode_time() > t

    def has_travelled(self, dist):
        """Returns true if the robot has driven `dist` centimetres driving the
        current mode (assuming it is driving straight) and false otherwise."""
        return self.has_elapsed(self.dist_to_time(dist))

    def has_rotated(self, angle):
        """Returns true if the robot has rotated by `angle` degrees during the
        current mode (assuming it is pivoting) and false otherwise."""
        t = self.angle_to_time(angle)
        return self.has_elapsed(t)

    def at_right_angle(self):
        """Returns true if the robot has rotated 90 degrees during the current
        mode (assuming it is pivoting) and false otherwise."""
        return self.has_rotated(90)

    # Subclasses should override the following three methods and `loop`.

    def move(self):
        """Makes Myro calls to move the robot according to the current mode.
        Called when the mode is begun and whenever the program is resumed."""
        pass

    def begin_mode(self):
        """Called when a new mode is begun."""
        pass

    def end_mode(self):
        """Called when the mode is about to switch."""
        pass


def obstacle_average():
    """Returns the average of the three obstacle sensor readings."""
    readings = myro.getObstacle()
    return sum(readings) / float(len(readings))
