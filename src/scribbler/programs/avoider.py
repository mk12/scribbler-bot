# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Makes the Scribbler Bot drive around objects."""

import myro

from scribbler.programs.base import BaseProgram

class Avoider(BaseProgram):

    """."""

    def __init__(self):
        """."""
        BaseProgram.__init__(self)

    def __call__(self, command):
        base_response = BaseProgram.__call__(self, command)
        if base_response:
            return base_response
        return "program-specific command"

    def start(self):
        BaseProgram.start(self)

    def stop(self):
        BaseProgram.stop(self)

    def reset(self):
        BaseProgram.reset(self)

    def loop(self):
        return BaseProgram.loop(self)
