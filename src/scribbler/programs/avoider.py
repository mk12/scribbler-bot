# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Makes the Scribbler Bot drive around an obstacle."""

from time import time

import myro

from scribbler.programs.base import angle_to_time, average, BaseProgram

# The minimum sensor reading that is interpreted as an obstacle.
OBSTACLE_THRESH = 2

# The amount to rotate counterclockwise by, in degrees, after seeing the
# obstacle. After rotating, the obstacle sensors will be checked again, and in
# this way we determine which side of the box to go around. The sensors are not
# very reliable when the board is not parallel to the obstacle, so we can't just
# compare the left and right sensors in the first reading.
COMPARE_ROTATION = 7

# How often to check to see if we are past the obstacle.
CHECK_INTERVAL = 1.0

# How long to drive to get past the edge of the box before resuming checking.
OVERSHOOT_FRONT_TIME = 2.0
OVERSHOOT_SIDE_TIME = 2.5

# Statuses to be displayed at the beginning of each mode.
STATUSES = {
    'fwd-1': "driving forward",
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
        self.reset()

    def reset(self):
        """Stops and resets the program to the first mode."""
        BaseProgram.reset(self)
        self.mode = 0
        self.x_pos = 0
        self.heading = 'up'
        self.start_time = 0
        self.pause_time = 0
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

    def has_rotated(self, angle):
        """Returns true if the robot has rotated by `angle` degrees during the
        current mode (assumign it is pivoting) and false otherwise."""
        return self.has_elapsed(angle_to_time(angle, self.speed))

    def at_right_angle(self):
        """Returns true if the robot has rotated 90 degrees during the current
        mode (assuming it is pivoting) and false otherwise."""
        return self.has_rotated(90)

    def see_obstacle(self):
        """Checks the obstacle sensors on the robot. Returns 'left', 'center',
        or 'right' if an obstacle is seen in one of those directions, and
        returns None if there is no obstacle."""
        readings = myro.getObstacle()
        return average(readings)
        # if max(readings) < OBSTACLE_THRESH:
        #     return None
        # difference = readings[2] - readings[0]
        # if difference > OBSTACLE_DIFF_THRESH:
        #     return 'right'
        # if difference < -OBSTACLE_DIFF_THRESH:
        #     return 'left'
        # return 'center'

    def drive(self, direction):
        """Makes the Myro call to drive the robot in the given direction."""
        if direction == 'fwd':
            myro.forward(self.speed)
        if direction == 'bwd':
            myro.backward(self.speed)
        if direction == 'ccw':
            myro.rotate(self.around_mult * self.speed)
        if direction == 'cw':
            myro.rotate(self.around_mult * -self.speed)

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
            d = self.see_obstacle()
            if d:
                self.first_obstacle_reading = d
                return self.goto_mode('ccw-c')
        if self.mode == 'ccw-c':
            if self.has_rotated(COMPARE_ROTATION):
                d = self.see_obstacle()
                if d > self.first_obstacle_reading:
                    self.around_mult = -1
                return self.goto_mode('ccw-1')
        if self.mode == 'ccw-1':
            if self.has_rotated(90 - self.around_mult*COMPARE_ROTATION):
                return self.goto_mode('fwd-2')
        if self.mode == 'fwd-2':
            if self.has_elapsed(CHECK_INTERVAL):
                return self.goto_mode('cw-1')
        if self.mode == 'cw-1':
            if self.at_right_angle():
                myro.stop()
                if self.see_obstacle():
                    return self.goto_mode('ccw-1')
                else:
                    return self.goto_mode('ccw-2')
        if self.mode == 'ccw-2':
            if self.at_right_angle():
                return self.goto_mode('fwd-3')
        if self.mode == 'fwd-3':
            if self.has_elapsed(OVERSHOOT_FRONT_TIME):
                return self.goto_mode('cw-2')
        if self.mode == 'cw-2':
            if self.at_right_angle():
                if self.side == 'front':
                    return self.goto_mode('fwd-4')
                else:
                    return self.goto_mode('fwd-5')
        if self.mode == 'fwd-4':
            if self.has_elapsed(OVERSHOOT_SIDE_TIME):
                self.side = 'side'
                return self.goto_mode('cw-1')
            if self.see_obstacle():
                return self.goto_mode('ccw-1')
        if self.mode == 'fwd-5':
            if self.has_elapsed(self.x_pos):
                return self.goto_mode('ccw-3')
        if self.mode == 'ccw-3':
            if self.at_right_angle():
                return self.goto_mode('fwd-1')

    def end_mode(self):
        """Called once when the current mode is about to be switched."""
        d = self.mode_direction()
        if d == 'fwd':
            if self.heading == 'out':
                self.x_pos += self.mode_time()
            elif self.heading == 'in':
                self.x_pos -= self.mode_time()
        elif d == 'bwd':
            if self.heading == 'out':
                self.x_pos -= self.mode_time()
            elif self.heading == 'in':
                self.x_pos += self.mode_time()
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
