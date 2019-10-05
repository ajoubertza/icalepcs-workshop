import socket
import time
from tango import EventType
from tango.test_utils import DeviceTestContext

from ps0b import PowerSupply


def test_calibrate():
    """Test device calibration and voltage reading."""
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.calibrate()
        assert proxy.voltage == 1.23


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def test_events():
    """Test change events occur."""
    results = []

    def callback(evt):
        if not evt.err:
            results.append(evt)

    port = get_open_port()
    with DeviceTestContext(PowerSupply, process=True, port=port) as proxy:
        eid = proxy.subscribe_event(
            "random", EventType.CHANGE_EVENT, callback, wait=True)
        # wait for events to happen
        time.sleep(2)
        assert len(results) > 1
        proxy.unsubscribe_event(eid)
