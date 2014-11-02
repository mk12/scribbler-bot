# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Mediates between the server and the currently executing program."""

from gevent import Greenlet, sleep
from gevent.queue import Queue

from scribbler.programs import avoider, tracie


# Map program IDs to their respective classes or functions.
PROGRAMS = {'avoid': avoider.Avoider, 'tracie': tracie.Tracie}

# This is the program that is initially active.
DEFAULT_PROGRAM = 'tracie'

# The prefix to a command which indicates a program switch.
PROGRAM_PREFIX = 'program:'

# Amount of time to sleep between main loop iterations (seconds).
LOOP_DELAY = 0.01


class Controller(object):

    """Manages a program's main loop in a Greenlet."""

    def __init__(self, program_id=DEFAULT_PROGRAM):
        """Creates a controller to control the specified program. The program
        doesn't start executing until the start method is called."""
        self.messages = Queue()
        self.program_id = program_id
        self.program = PROGRAMS[program_id]()
        self.green = None
        self.can_reset = False

    def start(self):
        """Starts (or resumes) the execution of the program."""
        self.green = Greenlet(self.main_loop)
        self.green.start()
        self.program.start()
        self.can_reset = True

    def stop(self):
        """Stops the execution of the program."""
        self.program.stop()
        if self.green:
            self.green.kill()

    def reset(self):
        """Stops the program and resets it to its initial state."""
        self.stop()
        self.program.reset()
        self.can_reset = False

    def switch_program(self, program_id):
        """Stops execution and switches to a new program."""
        self.stop()
        self.program_id = program_id
        self.program = PROGRAMS[program_id]()
        self.can_reset = False

    def main_loop(self):
        """Runs the program's loop method continously, collecting any returned
        messages into the messages queue."""
        while True:
            msg = self.program.loop()
            if msg:
                self.messages.put(msg)
            sleep(LOOP_DELAY)

    def __call__(self, command):
        """Accepts a command and either performs the desired action or passes
        the message on to the program. Returns a status message."""
        if command == 'short:sync':
            pid = self.program_id
            running = bool(self.green)
            can_reset = self.can_reset
            return "{} {} {}".format(pid, running, can_reset)
        if command == 'long:status':
            return self.messages.get()
        if command.startswith(PROGRAM_PREFIX):
            prog = command[len(PROGRAM_PREFIX):]
            self.switch_program(prog)
            return "switched to {}".format(prog)
        if command == 'control:start':
            if self.green:
                return "already running"
            self.start()
            return "program resumed"
        if command == 'control:stop':
            if not self.green:
                return "not running"
            self.stop()
            return "program paused"
        if command == 'control:reset':
            self.reset()
            return "program reset"
        return self.program(command)
