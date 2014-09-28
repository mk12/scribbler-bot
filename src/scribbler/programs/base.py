# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements common functionality for Scribbler programs."""

# import Myro

class BaseProgram(object):
    """A base program that handles some of the details that communication with
    the server involves."""

    def __init__(self, server):
        """Creates a new base program."""
        pass

    def __call__(self, command):
        """."""
        return "commanded base"

    # Subclasses should override the following four methods.

    def start(self):
        """Called when the controller is started."""
        pass

    def stop(self):
        """Called when the controller is stopped."""
        # Myro.stop()
        pass

    def reset(self):
        """Resets the program to its initial state."""
        pass

    def loop(self):
        """The main loop of the program."""
        return "long-polling update"
