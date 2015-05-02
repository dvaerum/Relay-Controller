from collections import deque
from threading import Thread
import time
from state_machine import StateMachine, RelayState
import sys
try:
    import RPIO as GPIO
except SystemError:
    import lib.fakegpio as GPIO


class Watt:
    __pulse = deque([])
    __kW = 0.0

    __event_function = None

    def add_pulse(self, gpio_id, value):
        # TODO: How to handle float overflow (time.perf_counter)
        # Mads (vismanden) siger at det aldrig sker
        self.__pulse.append(time.perf_counter())
        seconds = self.interval()
        if seconds >= 60:
            # 1st try
            # self.__kW = (len(self.__pulse) * 36)/seconds
            self.__kW = (len(self.__pulse)/seconds)/0.36

            if self.__event_function:
                self.__event_function(self.__kW, seconds)

            while self.interval() >= 60:
                self.__pulse.popleft()
        else:
            print("An Interrupt happened (%.2fs)" % seconds)
            sys.stdout.flush()

    def interval(self):
        # return self.__pulse[len(self.__pulse)-1]-self.__pulse[0]
        return self.__pulse[-1]-self.__pulse[0]

    def set_event_function(self, call_function):
        self.__event_function = call_function


class PI(Thread):
    """
    class Relay(object):
        __slots__ = ["watt", "switch_on", "switch_off", "GPIO", "number",
                     "timestamp_switch_on", "timestamp_switch_off"]
    """

    __watt = Watt()
    __state_machine = StateMachine()

    __relays = []
    __relays_count = 0

    __thread_relay = None

    def __init__(self, pin_interrupts):
        Thread.__init__(self)
        self.name = "Thread PI.run"  # Name this thread

        GPIO.add_interrupt_callback(pin_interrupts, self.__watt.add_pulse, edge='rising')
        self.__watt.set_event_function(self.__pass_watt)
        #self.__watt.set_event_function(self.print_info)

    def run(self):
        self.__state_machine.start()
        GPIO.wait_for_interrupts()

    def stop(self):
        GPIO.stop_waiting_for_interrupts()
        GPIO.cleanup()

    def add_relay(self, relay):
        # TODO: event, that shall wait on handle_relay

        for r in relay:
            self.__state_machine.add_relay(
                RelayState(r.kilo_watt,
                           r.switch_on,
                           r.switch_off,
                           r.gpio_pin,
                           r.relay_number))

    def __pass_watt(self, kilo_watt, interval_time):
        print("%.4f kW (%.2fs)" % (kilo_watt, interval_time))
        sys.stdout.flush()


        if self.__state_machine.is_started():
            if not self.__thread_relay or not self.__thread_relay.isAlive():
                self.__thread_relay = Thread(target=self.__state_machine.next,
                                            name="Thread StateMachine.next",
                                            args=(kilo_watt, interval_time))
                self.__thread_relay.start()


    """
    def add_relay(self, relay):
        # TODO: event, that shall wait on handle_relay

        for r in relay:
            index = -1
            for i in range(len(self.__relays)):
                if self.__relays[i].number == r.number:
                    index = i

            if index == -1:
                GPIO.setup(r.GPIO, GPIO.OUT)
                self.__relays.append(self.Relay())

            self.__relays[index].watt = r.watt
            self.__relays[index].switch_on = r.switch_on
            self.__relays[index].switch_off = r.switch_off
            self.__relays[index].number = r.number
            self.__relays[index].GPIO = r.GPIO
            self.__relays[index].timestamp_switch_on = 0.0
            self.__relays[index].timestamp_switch_off = 0.0

        self.__relays.sort(key=lambda t: t.number)

    def print_info(self, kilo_watt, interval_time):
        print("%s kW (%.2fs)" % (kilo_watt, interval_time))

        if len(self.__relays):
            if not self.__thread_relay or not self.__thread_relay.isAlive():
                self.__thread_relay = Thread(target=self.handle_relay,
                                            name="Thread PI.handle_relay",
                                            args=(kilo_watt, interval_time))
                self.__thread_relay.start()

    def handle_relay(self, kilo_watt, interval_time):
        # TODO: event, that shall wait on add_relay
        relay = self.__relays[self.__relays_count]

        if relay.watt <= kilo_watt and self.__relays_count < len(self.__relays):
            print("time.perf_counter() - relay.switch_on = %s\nrelay.timestamp_switch_on = %s\nself.__relays_count = %s" % (time.perf_counter() - relay.switch_on, relay.timestamp_switch_on, self.__relays_count))
            relay.timestamp_switch_off = 0.0
            if relay.timestamp_switch_on == 0.0:
                relay.timestamp_switch_on = time.perf_counter()
            elif relay.timestamp_switch_on <= time.perf_counter() - relay.switch_on:
                relay.timestamp_switch_on = 0.0
                print("GPIO %i: ON" % (relay.GPIO))
                self.__count(1)

        elif relay.watt > kilo_watt and self.__relays_count >= 0:
            print("time.perf_counter() - relay.switch_off = %s\nrelay.timestamp_switch_off = %s\nself.__relays_count = %s" % (time.perf_counter() - relay.switch_off, relay.timestamp_switch_off, self.__relays_count))
            relay.timestamp_switch_on = 0.0
            if relay.timestamp_switch_off == 0.0:
                relay.timestamp_switch_off = time.perf_counter()
            elif relay.timestamp_switch_off <= time.perf_counter() - relay.switch_off:
                relay.timestamp_switch_off = 0.0
                print("GPIO %i: OFF" % (relay.GPIO))
                self.__count(-1)
                GPIO.channel_to_gpio

    def __count(self, value):
        self.__relays_count += value
        if self.__relays_count < 0:
            self.__relays_count = 0
        elif self.__relays_count >= len(self.__relays):
            self.__relays_count = len(self.__relays)-1
    """