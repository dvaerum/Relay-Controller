__author__ = 'alt_mulig'

import unittest
from state_machine import RelayState
from state_machine import _ON
from state_machine import _OFF
from time import sleep


class TestRelayState(unittest.TestCase):
    def setUp(self):
        self.relay_state = RelayState(10, 3, 9, 11, 37)
        self.relay_state_1 = RelayState(10, 3.0, 9, 11, 1)
        self.relay_state_2 = RelayState(10,   5, 7, 10, 2)
        self.relay_state_3 = RelayState(10,   5, 7,  9, 3)

        self.relay_state_1.next = self.relay_state_2
        self.relay_state_2.prev = self.relay_state_1
        self.relay_state_2.next = self.relay_state_3
        self.relay_state_3.prev = self.relay_state_2

    def test_01_get_kilo_watt(self):
        self.assertEqual(self.relay_state.get_kilo_watt(), 10.0)

    def test_02_get_switch_on(self):
        self.assertEqual(self.relay_state.get_switch_on(), 3)

    def test_03_get_switch_off(self):
        self.assertEqual(self.relay_state.get_switch_off(), 9)

    def test_04_get_gpio_pin(self):
        self.assertEqual(self.relay_state.get_gpio_pin(), 11)

    def test_05_get_relay_number(self):
        self.assertEqual(self.relay_state.get_relay_number(), 37)

    def test_06_update(self):
        self.relay_state.update(8, 9, 3)
        self.assertTrue(self.relay_state.get_kilo_watt() == 8, True)
        self.assertTrue(self.relay_state.get_switch_on() == 9, True)
        self.assertTrue(self.relay_state.get_switch_off() == 3, True)

    def test_07_copy_to(self):
        RelayState(8, 9, 3, 11, 37).copy_to(self.relay_state)
        self.assertTrue(self.relay_state.get_kilo_watt() == 8, True)
        self.assertTrue(self.relay_state.get_switch_on() == 9, True)
        self.assertTrue(self.relay_state.get_switch_off() == 3, True)

    def test_08___return_state(self):
        pass

    def test_09___next_state(self):
        pass

    def test_10___prev_state(self):
        pass

    def test_11_force_state(self):
        # Test for exception then the input is not '_ON' or '_OFF'
        self.assertRaises(ValueError, self.relay_state.force_state, None)

        # Test relay_state_1
        self.assertEqual(self.relay_state_1.force_state(_ON),
                         self.relay_state_2)
        self.assertEqual(self.relay_state_1.force_state(_OFF),
                         self.relay_state_1)
        # Test relay_state_2
        self.assertEqual(self.relay_state_2.force_state(_ON),
                         self.relay_state_3)
        self.assertEqual(self.relay_state_2.force_state(_OFF),
                         self.relay_state_1)
        # Test relay_state_3
        self.assertEqual(self.relay_state_3.force_state(_ON),
                         self.relay_state_3)
        self.assertEqual(self.relay_state_3.force_state(_OFF),
                         self.relay_state_2)

    def test_12_run(self):
        self.assertEqual(self.relay_state_2.run(10.), self.relay_state_2)

        self.assertEqual(self.relay_state_1.run(9), self.relay_state_1)



if __name__ == '__main__':
    unittest.main()
