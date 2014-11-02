# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""..."""

from time import time

# import nomyro as myro
import myro

from scribbler.programs.base import BaseProgram


# Short codes for the parameters of the program.
PARAM_CODES = {
    'rad': 'circle_radius',
    'sl': 'side_length',
    'ow': 'other_wheel'
}


# Default values for the parameters of the program.
PARAM_DEFAULTS = {
    'circle_radius': 10,
    'side_length': 10,
    'other_wheel': 0
}


class Other(BaseProgram):
    
    """..."""

    def __init__(self):
        """..."""
        BaseProgram.__init__(self)
        self.params.update(PARAM_DEFAULTS)
        self.codes.update(PARAM_CODES)
        self.reset()

    def reset(self):
        """..."""
        self.pause_time = 0
        self.mode = 0
        self.start_time = 0

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
        starts the new mode immediately. Returns the new status."""
        myro.stop()
        # self.end_mode()
        self.mode = mode
        self.start_time = time()
        # self.begin_mode()
        self.move()
        return "next mode"

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

    def move(self):
        """..."""
        if self.mode in [0, 2, 4, 6]:
            myro.forward(self.speed)
        elif self.mode in [1, 3, 5, 7]:
            myro.rotate(self.speed)
        if self.mode == 8:
            myro.motors(self.speed, self.speed*self.params['other_wheel'])

    def loop(self):
        """..."""
        if self.mode in [0, 2, 4, 6]:
            if self.has_travelled(self.params['side_length']):
                return self.goto_mode(self.mode + 1)
        if self.mode in [1, 3, 5, 7]:
            if self.at_right_angle():
                return self.goto_mode(self.mode + 1)
        if self.mode == 8 and self.has_travelled(2*3.1415*self.params['circle_radius']):
            return self.goto_mode(0)
