#!/usr/bin/env python3
import enum
import random
from time import sleep
from tango.server import Device, attribute, command


class TrackingMode(enum.IntEnum):
    INDEPENDENT = 0  # must start at zero!
    SYNCED = 1  # and increment by 1


class PowerSupply(Device):

    @attribute(dtype=float)
    def voltage(self):
        return 1.23

    @command
    def calibrate(self):
        sleep(0.1)

    @attribute(
        dtype=float,
        polling_period=500,  # ms
        rel_change=1e-3)
    def random(self):
        return random.random()

    @attribute(dtype=TrackingMode)
    def output_tracking(self):
        return TrackingMode.SYNCED


if __name__ == '__main__':
    PowerSupply.run_server()
