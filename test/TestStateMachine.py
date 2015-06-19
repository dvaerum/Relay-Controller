__author__ = 'alt_mulig'

import unittest
from state_machine import RelayState
from state_machine import StateMachine


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.sm = StateMachine()

        # self.relay_state = RelayState(10, 3, 9, 11, 37)
        self.rs = [RelayState(10,   1, 2, 10, 1),
                   RelayState(10,   1, 2,  9, 2),
                   RelayState(10,   1, 2, 11, 3),
                   RelayState(10,   1, 2, 22, 4)]

        self.sm.add_relay(self.rs[1])
        self.sm.add_relay(self.rs[0])
        self.sm.add_relay(self.rs[3])
        self.sm.add_relay(self.rs[2])

    def test_01_start(self):
        self.assertEqual(self.sm._StateMachine__current_state, None)
        self.sm.start()
        self.sm.start()
        self.assertEqual(self.sm._StateMachine__current_state,
                         self.sm._StateMachine__start.next)

    def test_02_next(self):
        self.assertRaises(IndexError, self.sm.next, 10.5, None)
        self.sm.start()
        self.assertEqual(self.sm.next(10.5, None), None)

    def test_03_stop(self):
        self.sm.start()
        self.sm.stop()
        self.sm.stop()
        self.assertEqual(self.sm._StateMachine__current_state, None)

    def test_04_is_started(self):
        self.assertEqual(self.sm._StateMachine__current_state, None)
        self.sm.start()
        self.assertEqual(self.sm._StateMachine__current_state,
                         self.sm._StateMachine__start.next)

    def test_05_add_relay(self):
        # "cs" stands for "current_state"
        cs = self.sm._StateMachine__start
        while not cs.next:
            cs = cs.next
            i = cs.get_relay_number()-1
            self.assertEqual(cs.get_kill_watt(),    self.rs[i].get_kill_watt())
            self.assertEqual(cs.get_switch_on(),    self.rs[i].get_switch_on())
            self.assertEqual(cs.get_switch_off(),   self.rs[i].get_switch_off())
            self.assertEqual(cs.get_gpio_pin(),     self.rs[i].get_gpio_pin())
            self.assertEqual(cs.get_relay_number(), self.rs[i].get_relay_number())
            if i == 0:
                self.assertEqual(cs.prev.get_relay_number(), 0)
                self.assertEqual(cs.next.get_relay_number(), 2)
            elif i == len(self.rs)-1:
                self.assertEqual(cs.prev.get_relay_number(), i)
                self.assertEqual(cs.next.get_relay_number(), i+1)
            else:
                self.assertEqual(cs.prev.get_relay_number(), i)
                self.assertEqual(cs.next.get_relay_number(), i+1)

    def test_06_add_relay(self):
        self.sm.add_relay(self.rs[0])
        self.sm.add_relay(self.rs[1])
        self.sm.add_relay(self.rs[2])
        self.sm.add_relay(self.rs[3])

        self.test_05_add_relay()

    def test_07_add_relay(self):
        self.sm.add_relay(self.rs[3])
        self.sm.add_relay(self.rs[2])
        self.sm.add_relay(self.rs[1])
        self.sm.add_relay(self.rs[0])

        self.test_05_add_relay()

if __name__ == '__main__':
    unittest.main()
