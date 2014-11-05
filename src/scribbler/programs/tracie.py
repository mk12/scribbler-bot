# Copyright 2014 Mitchell Kember and Charles Bai. Subject to the MIT License.

"""Makes the Scribbler Bot trace shapes with a marker."""

import math
from time import time

from scribbler.programs.base import ModeProgram


# Short codes for the parameters of the program.
PARAM_CODES = {
    'rs': 'rotation_speed'
}


# Default values for the parameters of the program.
PARAM_DEFAULTS = {
    'rotation_speed': 0.5
}


class Tracie(ModeProgram):

    """Tracie takes a set of points as input and draws the shape with a pen."""

    def __init__(self):
        ModeProgram.__init__(self, 0)
        self.add_params(PARAM_DEFAULTS, PARAM_CODES)
        # TODO: how/when to set points?
        self.points = [(0, 0), (1, 1), (2, 0), (0, 0)]

    def reset(self):
        ModeProgram.reset(self)
        self.index = 1
        self.heading = 0
        self.rot_dir = 1
        self.go_for = 0

    @property
    def speed(self):
        if self.mode == 'rotate':
            return self.params['rotation_speed']
        return self.params['speed']

    def is_mode_done(self):
        """Returns true if the current mode is finished, and false otherwise.
        The 'halt' mode is never done."""
        z = self.mode == 0
        halt = self.mode == 'halt'
        return z or (not halt and self.has_elapsed(self.go_for))

    def next_mode(self):
        """Switches to the next mode and starts it."""
        if self.mode == 'halt':
            return
        if self.mode == 0 or self.mode == 'rotate':
            self.set_drive_time()
            self.goto_mode('drive')
        elif self.mode == 'drive':
            self.index += 1
            if self.index < len(self.points):
                self.set_rotate_time()
                self.goto_mode('rotate')
            else:
                self.goto_mode('halt')

    def set_drive_time(self):
        """Sets the time duration for which the robot should drive in order to
        get to the next point."""
        # TODO: implement this function
        # The robot is current at self.points[self.index-1].
        # It should drive to the point self.points[self.index].
        # Find the distance between these points, convert it to time, and then
        # store the result in self.go_for.
        x1, y1 = self.points[self.index -1]
        x2, y2 = self.points[self.index]
        distance = math.sqrt(math.pow((y2 - y1), 2) + math.pow((x2 - x1), 2))
        time = self.dist_to_time(distance)
        self.go_for = time
        

    def set_rotate_time(self):
        """Sets the time duration for which the robot should rotate in order to
        be facing the next point."""
        # TODO: implement this function
        # The robot is current at self.points[self.index-1].
        # It should turn to face the point self.points[self.index].
        # Find the angle that it must turn, convert it to time, and then store
        # the result in self.go_for.
        x1, y1 = self.points[self.index -1]
        x2, y2 = self.points[self.index]
        yDistance = y2 - y1
        xDistance = x2 - x1
        angle = math.atan2(yDistance/xDistance)

        # Clockwise is negative and counterclockwise is positive
        cwRotation = -1*(self.heading - angle)

        if fabs(cwRotation) <= math.pi:
            self.heading = angle
            time = self.radians_to_time(cwRotation)
            self.go_for = time

        elif fabs(cwRotation) > math.pi:
            self.heading = angle
            time = self.radians_to_time(2*math.pi - cwRotation)
            self.go_for = time
            

    def move(self):
        """Makes Myro calls to move the robot according to the current mode.
        Called when the mode is begun and whenever the program is resumed."""
        ModeProgram.move(self)
        if self.mode == 'halt':
            myro.stop()
        if self.mode == 'drive':
            myro.forward(self.speed)
        if self.mode == 'rotate':
            myro.rotate(self.rot_dir * self.speed)

    def status(self):
        """Return the status message that should be displayed at the beginning
        of the current mode."""
        # return STATUSES.get(self.mode, "bad mode" + str(self.mode))
        return self.mode

    def loop(self):
        ModeProgram.loop(self)
        if self.is_mode_done():
            self.next_mode()
            return self.status()
