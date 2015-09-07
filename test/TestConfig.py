__author__ = 'Dennis Vestergaard Værum'

import unittest
from os.path import exists
from os import remove

from lib.client.config import Config

working_config_file = \
"""
[Relay1]
watt = 10
koble_ind = 30
koble_ud = 90

[Relay3]
watt = 10
koble_ind = 30
koble_ud = 90

[Relay2]
watt = 10
koble_ind = 30
koble_ud = 90

[Relay4]
watt = 10
koble_ind = 30
koble_ud = 90
"""

fail1_config_file = \
"""
[Relay1]
watt = 10.0
koble_ind = 31,0
koble_ud = 81

[Relay3]
watt = 10
koble_ind = 33

[Relay2]
watt = 10
koble_ind =
koble_ud = 82

[Relay4]
watt = 10
koble_ind = 34
koble_ud = 84
"""


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.filename = "etc/test.conf"
        self.config = Config(self.filename)
        if exists(self.filename):
            remove(self.filename)

    def tearDown(self):
        remove(self.filename)

    # Part 1
    def test_01_load(self):
        # Testing if file exist
        self.assertRaises(FileNotFoundError, self.config.load)

        # Testing if Relays is configured
        f = open("etc/test.conf", "w")
        self.assertRaises(ImportError, self.config.load)

        # Test if the config file was loaded
        f.write(working_config_file)
        f.flush()
        self.assertEqual(self.config.load(), None)

    # Part 2
    def test_02_loadad(self):
        f = open("etc/test.conf", "w")
        f.write(fail1_config_file)
        f.flush()

        self.assertEqual(self.config.load(), None)


if __name__ == '__main__':
    unittest.main()
