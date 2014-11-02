# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements common functionality for Scribbler programs."""

import time


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
        self.params = PARAM_DEFAULTS
        self.codes = PARAM_CODES

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

    def time_to_dist(self, time):
        """The inverse of dist_to_time."""
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
            if value == "" or value == "?":
                return name + " = " + str(self.params[name])
            try:
                n = float(value)
            except ValueError:
                return "NaN: " + value
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


class SeqProgram(BaseProgram):

    """A program that interprets a sequence of instructions.

    The sequence is a list of modes. A mode is represented by a triple of the
    form `(i, c, p, s)` where `i` is an instruction string, `c` is the
    condition, `p` is the parameter of the condition, and `s` is the status
    message to display. The program beings by performing the instruction of the
    first mode, and it moves on to the next mode when the condition of the first
    mode is met. After the last mode, we return to the first mode.
    """

    def __init__(self, seq):
        """Creates a program that interprets the given sequence."""
        BaseProgram.__init__(self)
        self.seq = seq
        self.build_maps()
        self.reset()

    def build_maps(self):
        self.instructions = {
            'fwd': lambda t: myro.forward(self.speed),
            'bwd': lambda t: myro.backward(self.speed),
            'ccw': lambda t: myro.rotate(self.speed),
            'cw': lambda t: myro.rotate(-self.speed)
        }
        self.conditions = {
            'ir>': lambda v: average(myro.getObstacle()) > v,
            'time': lambda t: self.time > t,
            'dist': lambda d: self.time > dist_to_time(d, self.speed),
            'angle': lambda a: self.time > angle_to_time(a, self.speed),
            'forever': lambda _: False,
        }

    @property
    def time(self):
        """Returns the time elapsed since the current mode was started."""
        return time.time() - self.start_time

    def increment_mode(self):
        """Increments the mode index (wrapping around if necessary), updates
        mode variables, and resets the timer."""
        myro.stop()
        self.mode_ind += 1
        self.mode_ind %= len(self.seq)
        self.i, self.c, self.p, self.s = self.seq[self.mode_ind]
        self.start_time = time.time()

    def reset(self):
        """Resets the program to the first mode."""
        BaseProgram.reset(self)
        self.mode_ind = -1

    def stop(self):
        """Record the time when the program is paused."""
        BaseProgram.stop(self)
        self.pause_time = time.time()

    def start(self):
        """Fixes the start time so that the pause doesn't count towards the
        elapsed time, and continues the previous motion of the robot."""
        BaseProgram.start(self)
        self.start_time += time.time() - self.pause_time
        self.perform_instruction()

    def perform_instruction(self):
        """Performs the instruction dictated by the current mode."""
        self.instructions[self.i](self.p)

    def condition_satisfied(self):
        """Returns whether the current mode's condition is satisfied."""
        return self.mode_ind == -1 or self.conditions[self.c](self.p)

    def loop(self):
        """Advances to the next mode and performs the instruction when it is
        time (when the condition is met), otherwise does nothing."""
        BaseProgram.loop(self)
        if self.condition_satisfied():
            self.increment_mode()
            self.perform_instruction()
            return self.s

    def __call__(self, command):
        base_response = BaseProgram.__call__(self, command)
        if base_response:
            return base_response
        return "unrecognized command"


def average(xs):
    """Returns the average of a list of floating-point values."""
    return sum(xs) / float(len(xs))

