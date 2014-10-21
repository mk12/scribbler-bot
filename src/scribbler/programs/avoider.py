# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Makes the Scribbler Bot drive around an obstacle."""

from time import time

import myro

from scribbler.programs.base import average, BaseProgram


# Short codes for the parameters of the program.
PARAM_CODES = {
    'sd': 'obstacle_slowdown',
    'ot': 'obstacle_thresh',
    'cr': 'compare_rotation',
    'nn': 'not_ninety',
    'cd': 'check_dist',
    'of': 'overshoot_front',
    'os': 'overshoot_side'
}

#att 0.0072 good for 0.2 speed


# Default values for the parameters of the program.
PARAM_DEFAULTS = {
    'obstacle_slowdown': 0.2,
    'obstacle_thresh': 2, # from 0 to 6400
    'compare_rotation': 25, # deg
    'not_ninety': 80, # deg
    'check_dist': 6.0, # cm
    'overshoot_front': 10.0, # cm
    'overshoot_side': 10.0, # cm
}


# Statuses to be displayed at the beginning of each mode.
STATUSES = {
    'fwd-1': "driving forward",
    'ccw-c': "checking slant",
    'cw-c': "unchecking slant",
    'ccw-1': "turning 90 ccw",
    'fwd-2': "driving along",
    'cw-1': "checking obstacle",
    'ccw-2': "unturning",
    'fwd-3': "going further",
    'cw-2': "returning",
    'fwd-4': "past front edge",
    'fwd-5': "past back edge",
    'ccw-3': "straightening up"
}


class Avoider(BaseProgram):

    """The third generation of the object avoidance program."""

    def __init__(self):
        """Creates a new Avoider in a reset state."""
        BaseProgram.__init__(self)
        self.params.update(PARAM_DEFAULTS)
        self.codes.update(PARAM_CODES)
        self.reset()

    def reset(self):
        """Stops and resets the program to the first mode."""
        BaseProgram.reset(self)
        self.mode = 0
        self.temporal_x = 0
        self.heading = 'up'
        self.start_time = 0
        self.pause_time = 0
        self.around_mult_f = 1
        self.around_mult = 1
        self.first_obstacle_reading = 0
        self.side = 'front'

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
        self.end_mode()
        self.mode = mode
        self.start_time = time()
        self.begin_mode()
        self.move()
        return self.status()

    def mode_direction(self):
        """Returns the identifier of the direction of motion for this mode."""
        if self.mode == 0:
            return None
        return self.mode.split('-')[0]

    def move(self):
        """Makes Myro calls to move the robot according to the current mode.
        Called when the mode is begun and whenever the program is resumed."""
        self.drive(self.mode_direction())

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
        return self.has_elapsed(self.angle_to_time(angle))

    def at_right_angle(self):
        """Returns true if the robot has rotated 90 degrees during the current
        mode (assuming it is pivoting) and false otherwise."""
        return self.has_rotated(90)

    def obstacle(self):
        """Returns the average of the obstacle sensor readings."""
        return average(myro.getObstacle())

    def drive(self, direction):
        """Makes the Myro call to drive the robot in the given direction."""
        if self.mode == 'fwd-1':
            speed = self.params['obstacle_slowdown']
        else:
            speed = self.speed
        if direction == 'fwd':
            myro.forward(speed)
        if direction == 'bwd':
            myro.backward(speed)
        if direction == 'ccw':
            myro.rotate(self.around_mult * speed)
        if direction == 'cw':
            myro.rotate(self.around_mult * -speed)

    def status(self):
        """Return the status message that should be displayed at the beginning
        of the current mode."""
        return STATUSES.get(self.mode, "bad mode" + str(self.mode))

    def begin_mode(self):
        """Called exactly once when each mode is begun."""
        pass

    def loop(self):
        """The main loop of the program (executes continuosly)."""
        BaseProgram.loop(self)
        if self.mode == 0:
            return self.goto_mode('fwd-1')
        if self.mode == 'fwd-1':
            d = self.obstacle()
            if d > self.params['obstacle_thresh']:
                self.first_obstacle_reading = d
                return self.goto_mode('ccw-c')
        if self.mode == 'ccw-c':
            if self.has_rotated(self.params['compare_rotation']):
                myro.stop()
                d = self.obstacle()
                if d < self.first_obstacle_reading:
                    self.around_mult_f = 1
                else:
                    self.around_mult_f = -1
                return self.goto_mode('cw-c')
        if self.mode == 'cw-c':
            if self.has_rotated(self.params['compare_rotation']):
                self.around_mult = self.around_mult_f
                return self.goto_mode('ccw-1')
        if self.mode == 'ccw-1':
            if self.at_right_angle():
                return self.goto_mode('fwd-2')
        if self.mode == 'fwd-2':
            if self.has_travelled(self.params['check_dist']):
                return self.goto_mode('cw-1')
        if self.mode == 'cw-1':
            if self.at_right_angle():
                myro.stop()
                if self.obstacle() > self.params['obstacle_thresh']:
                    return self.goto_mode('ccw-1')
                else:
                    return self.goto_mode('ccw-2')
        if self.mode == 'ccw-2':
            if self.at_right_angle():
                return self.goto_mode('fwd-3')
        if self.mode == 'fwd-3':
            if self.has_travelled(self.params['overshoot_front']):
                return self.goto_mode('cw-2')
        if self.mode == 'cw-2':
            if self.at_right_angle():
                if self.side == 'front':
                    return self.goto_mode('fwd-4')
                else:
                    return self.goto_mode('fwd-5')
        if self.mode == 'fwd-4':
            if self.has_travelled(self.params['overshoot_side']):
                self.side = 'side'
                return self.goto_mode('cw-1')
            if self.obstacle():
                return self.goto_mode('ccw-1')
        if self.mode == 'fwd-5':
            if self.has_elapsed(self.temporal_x):
                return self.goto_mode('ccw-3')
        if self.mode == 'ccw-3':
            if self.at_right_angle():
                self.reset()
                self.start()
                return "restarting program"

    def end_mode(self):
        """Called once when the current mode is about to be switched."""
        if self.mode in ['fwd-1', 'ccw-c', 'cw-c']:
            return
        d = self.mode_direction()
        if d == 'fwd':
            if self.heading == 'out':
                self.temporal_x += self.mode_time()
            elif self.heading == 'in':
                self.temporal_x -= self.mode_time()
        elif d == 'bwd':
            if self.heading == 'out':
                self.temporal_x -= self.mode_time()
            elif self.heading == 'in':
                self.temporal_x += self.mode_time()
        elif d == 'ccw':
            if self.heading == 'up':
                self.heading = 'out'
            elif self.heading == 'in':
                self.heading = 'up'
        elif d == 'cw':
            if self.heading == 'up':
                self.heading = 'in'
            elif self.heading == 'out':
                self.heading = 'up'
