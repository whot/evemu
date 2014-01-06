from multiprocessing import Process, Queue, Event

import re
import tempfile
import unittest

import evemu
import evemu.testing.testcase


def record(recording_started, device_node, q):
    """
    Runs the recorder in a separate process because the evemu API is a
    blocking API.
    """
    device = evemu.Device(device_node)
    with tempfile.TemporaryFile(mode='rt') as event_file:
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

class DeviceActionTestCase(evemu.testing.testcase.BaseTestCase):
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
        with tempfile.TemporaryFile(mode='rt') as t:
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


class DevicePropertiesTestCase(evemu.testing.testcase.BaseTestCase):
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
        self.assertEqual(self._device.version, 0x10000)

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
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.get_abs_minimum(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("min"))

    def test_get_abs_maximum(self):
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.get_abs_maximum(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("max"))

    def test_get_abs_fuzz(self):
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.get_abs_fuzz(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("fuzz"))

    def test_get_abs_flat(self):
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.get_abs_flat(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("flat"))

    def test_get_abs_resolution(self):
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.get_abs_resolution(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("res"))

    def test_has_prop(self):
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.has_prop(x)) for x in keys)

        self.assertEqual(results, self.get_expected_propbits())

    def test_has_event_ev_abs(self):
        ev_abs = evemu.const.event_types["EV_ABS"]
        keys = evemu.const.absolute_axes.values()
        results = dict((x, self._device.has_event(ev_abs, x)) for x in keys)

        self.assertEqual(results, self.get_expected_absbits())

    def test_has_event_ev_key(self):
        ev_key = evemu.const.event_types["EV_KEY"]
        keys = evemu.const.buttons.values()
        results = dict((x, self._device.has_event(ev_key, x)) for x in keys)

        self.assertEqual(results, self.get_expected_keybits())


if __name__ == "__main__":
    unittest.main()
