
from evemu.testing import testcase
from multiprocessing import Process, Queue, Event

import evemu
import os
import re
import tempfile
import unittest


def record(recording_started, device_node, q):
    """
    Runs the recorder in a separate process because the evemu API is a
    blocking API.
    """
    device = evemu.Device(device_node)
    with tempfile.TemporaryFile() as event_file:
        recording_started.set()
        device.record(event_file, 1000)
        event_file.flush()
        event_file.seek(0)
        outdata = event_file.readlines()
        q.put(outdata)

def strip_comments(data):
    """
    Strip comments, superfluous whitespaces and empty lines from the data.
    """
    stripped_data = []
    for line in data:
        line = line.partition("#")[0].strip()
        if len(line) > 0:
            stripped_data.append(line)
    return stripped_data

def extract_events(data):
    """
    Extract the actual event part from an event recording.
    """
    return [line for line in data if line.startswith("E:")]

class DeviceActionTestCase(testcase.BaseTestCase):
    """
    Verifies the high-level Device functions (create, describe, play, record).
    """

    def test_construct_from_dev_node_name(self):
        """
        Verifies a Device can be constructed from an existing input device node
        name.
        """
        d = evemu.Device("/dev/input/event0")

    def test_construct_from_dev_node_file(self):
        """
        Verifies a Device can be constructed from an existing input device node
        file object.
        """
        d = evemu.Device(open("/dev/input/event0"))

    def test_construct_from_prop_file_name(self):
        """
        Verifies a device can be constructed from an evemu prop file name.
        """
        d = evemu.Device(self.get_device_file())

    def test_construct_from_prop_file_file(self):
        """
        Verifies a device can be constructed from an evemu prop file file
        object.
        """
        d = evemu.Device(open(self.get_device_file()))

    def test_describe(self):
        """
        Verifies that a device description can be correctly extracted from a
        Device.
        """
        # Get original description
        with open(self.get_device_file()) as f:
	     data = strip_comments(f.readlines())

        # Create a pseudo device with that description
        d = evemu.Device(self.get_device_file())

        # get the description to a temporary file
        with tempfile.TemporaryFile() as t:
            d.describe(t)

            # read in the temporary file and compare to the original
            t.flush()
            t.seek(0)
            newdata = strip_comments(t.readlines())
            self.assertEquals(data, newdata)

    def test_play_and_record(self):
        """
        Verifies that a Device and play back prerecorded events.
        """
        device = evemu.Device(self.get_device_file())
        devnode = device.devnode
        events_file = self.get_events_file()
        # device.record() calls evemu_record() and is thus missing the
        # description that the input file has
        with open(events_file) as e:
            indata = extract_events(strip_comments(e.readlines()))

        recording_started = Event()
        q = Queue()
        record_process = Process(target=record,
                                 args=(recording_started, devnode, q))
        record_process.start()
        recording_started.wait(100)
        device.play(open(events_file))

        outdata = strip_comments(q.get())
        record_process.join()

        self.assertEquals(len(indata), len(outdata))
        fuzz = re.compile("E: \d+\.\d+ (.*)")
        for i in range(len(indata)):
            lhs = fuzz.match(indata[i])
            self.assertTrue(lhs)
            rhs = fuzz.match(outdata[i])
            self.assertTrue(rhs)
            self.assertEquals(lhs.group(1), rhs.group(1))


class DevicePropertiesTestCase(testcase.BaseTestCase):
    """
    Verifies the workings of the various device property accessors.
    """

    def setUp(self):
        super(DevicePropertiesTestCase, self).setUp()
        self._device = evemu.Device(self.get_device_file())

    def tearDown(self):
        del self._device
        super(DevicePropertiesTestCase, self).tearDown()

    def test_version(self):
        self.assertEqual(self._device.version, 0)

    def test_name(self):
        self.assertEqual(self._device.name, "N-Trig-MultiTouch-Virtual-Device")

    def test_id_bustype(self):
        self.assertEqual(self._device.id_bustype, 3)

    def test_id_vendor(self):
        self.assertEqual(hex(self._device.id_vendor), "0x1b96")

    def test_id_product(self):
        self.assertEqual(self._device.id_product, 1)

    def test_id_version(self):
        self.assertEqual(self._device.id_version, 272)

    def test_get_abs_minimum(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self._device.get_abs_minimum(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_maximum(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9600, 7200, 0, 0, 0, 0,
            7200, 1, 7200, 0, 9600, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9600,
            0, 0,
            ]
        # Skipping the entry for ABS_CNT; some times it's 0, sometimes a very
        # large negative number.
        results = [self._device.get_abs_maximum(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results[:-1], expected[:-1])

    def test_get_abs_fuzz(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 75, 78, 0, 0, 0, 0, 150,
            0, 78, 0, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 0, 0, 
            ]
        results = [self._device.get_abs_fuzz(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_flat(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self._device.get_abs_flat(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_get_abs_resolution(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self._device.get_abs_resolution(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_prop(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self._device.has_prop(x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_event_ev_abs(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1,
            1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
            ]
        results = [self._device.has_event(evemu.const.event_types["EV_ABS"], x) 
                   for x in evemu.const.absolute_axes.values()]
        self.assertEqual(results, expected)

    def test_has_event_ev_key(self):
        expected = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ]
        results = [self._device.has_event(evemu.const.event_types["EV_KEY"], x) 
                   for x in evemu.const.buttons.values()]
        self.assertEqual(results, expected)


if __name__ == "__main__":
    unittest.main()
