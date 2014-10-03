# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Provides no-op implementations of Myro functions for testing purposes."""

import time


def forward(speed):
    pass


def backward(speed):
    pass


def rotate(speed):
    pass


def stop():
    pass


def beep():
    pass


def getObstacle():
    return [4000]


def getInfo():
    return "myro info"
