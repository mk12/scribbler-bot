# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""..."""

from time import time

from scribbler.programs.base import BaseProgram


# Short codes for the parameters of the program.
PARAM_CODES = {
    'rs': 'rotation_speed'
}


# Default values for the parameters of the program.
PARAM_DEFAULTS = {
    'rotation_speed': 0.5
}


class Tracie(BaseProgram):

    """..."""

    def __init__(self):
        BaseProgram.__init__(self)
        # TODO: how/when to set points?
        self.points = []
        self.params.update(PARAM_DEFAULTS)
        self.codes.update(PARAM_CODES)
        self.reset()

    def reset(self):
        """."""
        BaseProgram.reset(self)
        self.index = 0
        self.heading = 0
        self.pause_time = 0
        self.start_time = 0
        self.rot_dir = 1
        self.move_time = 0
        self.mode = 'halt'

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

    @property
    def speed(self):
        """Returns the nominal speed of the robot."""
        if self.mode == 'rotate':
            return self.params['rotation_speed']
        return self.params['speed']

    def next_mode(self):
        """."""
        myro.stop()
        self.end_mode()
        # TODO: clean this up
        if self.mode == 'drive':
            self.index += 1
            if self.index == len(self.points):
                self.mode = 'halt'
            else:
                self.set_rotate_time()
                self.mode = 'rotate'
        elif self.mode == 'rotate':
            self.set_drive_time()
            self.mode = 'drive'
        self.start_time = time()
        self.begin_mode()
        self.move()
        return self.status()

    def set_drive_time(self):
        # set self.move_time
        # (use self.dist_to_time(d)
        pass

    def set_rotate_time(self):
        # self.angle_to_time(a)
        pass

    def move(self):
        """Makes Myro calls to move the robot according to the current mode.
        Called when the mode is begun and whenever the program is resumed."""
        if self.mode == 'halt':
            myro.stop()
        if self.mode == 'drive':
            myro.forward(self.speed)
        if self.mode == 'rotate':
            self.rotate(self.rot_mult * self.speed)

    def mode_time(self):
        """Returns the time that has elapsed since the mode begun."""
        return time() - self.start_time

    def has_elapsed(self, t):
        """Returns true if `t` seconds have elapsed sicne the current mode begun
        and false otherwise."""
        return self.mode_time() > t

    def status(self):
        """Return the status message that should be displayed at the beginning
        of the current mode."""
        # return STATUSES.get(self.mode, "bad mode" + str(self.mode))
        return "something"

    def begin_mode(self):
        """Called exactly once when each mode is begun."""
        pass

    def loop(self):
        """The main loop of the program (executes continuosly)."""
        BaseProgram.loop(self)
        # stuff

    def end_mode(self):
        """..."""
        if self.mode in ['drive', 'rotate']:
            if self.has_elapsed(self.move_time):
                return self.next_mode()
