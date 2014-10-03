# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Makes the Scribbler Bot drive around an obstacle."""

import myro

from scribbler.programs.base import SeqProgram


seq = [
    ('fwd', 'ir>', 1000, "driving forward"),
    ('bwd', 'dist', 10, "detected obstacle"),
    ('ccw', 'angle', 90, "first turn"),
    ('fwd', 'dist', 25, "driving along front"),
    ('cw', 'angle', 90, "turning front corner"),
    ('fwd', 'dist', 50, "driving along side"),
    ('cw', 'angle', 90, "turning back corner"),
    ('fwd', 'dist', 25, "driving along back"),
    ('ccw', 'angle', 90, "returning to path")
]


def Avoider():
    """Creates a sequential Program based on the Avoider sequence."""
    return SeqProgram(seq)
