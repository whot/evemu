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

    def test_construct_from_prop_file_name_no_create(self):
        """
        Verifies a device can be constructed from an evemu prop file name,
        without creating a uinput device.
        """
        d = evemu.Device(self.get_device_file(), create=False)

    def test_construct_from_prop_file_file(self):
        """
        Verifies a device can be constructed from an evemu prop file file
        object.
        """
        d = evemu.Device(open(self.get_device_file()))

    def test_construct_from_prop_file_file_nocreate(self):
        """
        Verifies a device can be constructed from an evemu prop file file
        object, without creating a uinput device.
        """
        d = evemu.Device(open(self.get_device_file()), create=False)

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

    def test_read_events(self):
        device = evemu.Device(self.get_device_file(), create=False)
        events_file = self.get_events_file()
        with open(events_file) as ef:
            events = [e for e in device.events(ef)]
            self.assertTrue(len(events) > 1)

    def test_read_events_twice(self):
        device = evemu.Device(self.get_device_file(), create=False)
        events_file = self.get_events_file()
        with open(events_file) as ef:
            e1 = [(e.type, e.code, e.value) for e in device.events(ef)]
            e2 = [(e.type, e.code, e.value) for e in device.events(ef)]
            self.assertEquals(len(e1), len(e2))
            self.assertEquals(e1, e2)

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
        self.assertEqual(self._device.id_vendor, 0x1b96)

    def test_id_product(self):
        self.assertEqual(self._device.id_product, 1)

    def test_id_version(self):
        self.assertEqual(self._device.id_version, 272)

    def test_get_abs_minimum(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.get_abs_minimum(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("min"))

    def test_get_abs_maximum(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.get_abs_maximum(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("max"))

    def test_get_abs_fuzz(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.get_abs_fuzz(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("fuzz"))

    def test_get_abs_flat(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.get_abs_flat(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("flat"))

    def test_get_abs_resolution(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.get_abs_resolution(x)) for x in keys)

        self.assertEqual(results, self.get_expected_abs("res"))

    def test_has_prop(self):
        propmax = evemu.input_prop_get_value("INPUT_PROP_MAX")
        keys = range(0, propmax + 1)
        results = dict((x, self._device.has_prop(x)) for x in keys)

        self.assertEqual(results, self.get_expected_propbits())

    def test_has_event_ev_abs(self):
        absmax = evemu.event_get_value("EV_ABS", "ABS_MAX")
        keys = range(0, absmax + 1)
        results = dict((x, self._device.has_event("EV_ABS", x)) for x in keys)

        self.assertEqual(results, self.get_expected_absbits())

    def test_has_event_ev_key(self):
        keymax = evemu.event_get_value("EV_KEY", "KEY_MAX")
        keys = range(0, keymax + 1)
        results = dict((x, self._device.has_event("EV_KEY", x)) for x in keys)

        self.assertEqual(results, self.get_expected_keybits())

    def test_event_names(self):
        self.assertEqual(evemu.event_get_value("EV_SYN"), 0x00)
        self.assertEqual(evemu.event_get_value("EV_KEY"), 0x01)
        self.assertEqual(evemu.event_get_value("EV_ABS"), 0x03)
        self.assertEqual(evemu.event_get_value("EV_FOO"), None)
        self.assertEqual(evemu.event_get_value(1), 1)
        self.assertEqual(evemu.event_get_value(100), None)

        self.assertEqual(evemu.event_get_value("EV_SYN", "SYN_REPORT"), 0x00)
        self.assertEqual(evemu.event_get_value("EV_KEY", "KEY_Z"), 44)
        self.assertEqual(evemu.event_get_value("EV_ABS", "ABS_X"), 0x00)
        self.assertEqual(evemu.event_get_value("EV_ABS", "ABS_FOO"), None)
        self.assertEqual(evemu.event_get_value(1), 1)
        self.assertEqual(evemu.event_get_value(100), None)

        self.assertEqual(evemu.event_get_name(0x00), "EV_SYN")
        self.assertEqual(evemu.event_get_name(0x01), "EV_KEY")
        self.assertEqual(evemu.event_get_name(0x03), "EV_ABS")
        self.assertEqual(evemu.event_get_name(0xFFFF), None)
        self.assertEqual(evemu.event_get_name("foo"), None)
        self.assertEqual(evemu.event_get_name("EV_SYN"), "EV_SYN")

        self.assertEqual(evemu.event_get_name("EV_SYN", 0x00), "SYN_REPORT")
        self.assertEqual(evemu.event_get_name("EV_REL", 0x01), "REL_Y")
        self.assertEqual(evemu.event_get_name("EV_ABS", 0x00), "ABS_X")
        self.assertEqual(evemu.event_get_name("EV_ABS", 0xFFFF), None)
        self.assertEqual(evemu.event_get_name("EV_ABS", "foo"), None)
        self.assertEqual(evemu.event_get_name("EV_ABS", "ABS_X"), "ABS_X")

        self.assertEqual(evemu.event_get_name(None), None)
        self.assertEqual(evemu.event_get_name(None, None), None)

    def test_prop_names(self):
        self.assertEqual(evemu.input_prop_get_value("INPUT_PROP_POINTER"), 0x00)
        self.assertEqual(evemu.input_prop_get_value("INPUT_PROP_DIRECT"), 0x01)
        self.assertEqual(evemu.input_prop_get_value("INPUT_PROP_FOO"), None)
        self.assertEqual(evemu.input_prop_get_value(1), 1)
        self.assertEqual(evemu.input_prop_get_value(None), None)

        self.assertEqual(evemu.input_prop_get_name(0x00), "INPUT_PROP_POINTER")
        self.assertEqual(evemu.input_prop_get_name(0x01), "INPUT_PROP_DIRECT")
        self.assertEqual(evemu.input_prop_get_name(-1), None)
        self.assertEqual(evemu.input_prop_get_name("foo"), None)
        self.assertEqual(evemu.input_prop_get_name(None), None)

    def test_event_matching(self):
        e = evemu.InputEvent(0, 0, 0x01, 44, 0)
        self.assertTrue(e.matches("EV_KEY"))
        self.assertTrue(e.matches("EV_KEY", "KEY_Z"))
        self.assertTrue(e.matches(0x01))
        self.assertTrue(e.matches(0x01, 44))
        self.assertTrue(e.matches("EV_KEY", 44))
        self.assertTrue(e.matches(0x01, "KEY_Z"))

        for t in range(-1, 0xff):
            for c in range(-1, 0xff):
                if t != e.type or c != e.code:
                    self.assertFalse(e.matches(t, c))

        e = evemu.InputEvent(0, 0, 0x02, 0x01, 0)
        self.assertTrue(e.matches("EV_REL"))
        self.assertTrue(e.matches("EV_REL", "REL_Y"))
        self.assertTrue(e.matches(0x02))
        self.assertTrue(e.matches(0x02, 0x01))
        self.assertTrue(e.matches("EV_REL", 0x01))
        self.assertTrue(e.matches(0x02, "REL_Y"))

        for t in range(-1, 0xff):
            for c in range(-1, 0xff):
                if t != e.type or c != e.code:
                    self.assertFalse(e.matches(t, c))

        e = evemu.InputEvent(0, 0, 0x03, 0x00, 0)
        self.assertTrue(e.matches("EV_ABS"))
        self.assertTrue(e.matches("EV_ABS", "ABS_X"))
        self.assertTrue(e.matches(0x03))
        self.assertTrue(e.matches(0x03, 0x00))
        self.assertTrue(e.matches("EV_ABS", 0x00))
        self.assertTrue(e.matches(0x03, "ABS_X"))

        for t in range(-1, 0xff):
            for c in range(-1, 0xff):
                if t != e.type or c != e.code:
                    self.assertFalse(e.matches(t, c))

if __name__ == "__main__":
    unittest.main()
