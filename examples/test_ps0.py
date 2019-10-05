from tango.test_utils import DeviceTestContext

from ps0 import PowerSupply


def test_calibrate():
    """Test device calibration and voltage reading."""
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.calibrate()
        assert proxy.voltage == 1.23
