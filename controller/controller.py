"""Module for simulating an engine controller"""

__author__ = "Jackson Harmer"
__copyright__ = "Copyright (c) 2020 Jackson Harmer. All rights reserved."
__license__ = "MIT"
__version__ = "0.1"

from simple_pid import PID
from typing import List
import i2c_comms as i2c
import RPi.GPIO as GPIO
import time


class DTC:
    """
    Class representing a diagnostic trouble code.

    Contains an integer identifier and a string description
    """

    number: int
    message: str

    def __init__(self, num: int, mesg: str):
        self.number = num
        self.message = mesg


# Global tuning parameters
_ACCEL_DIFF_RANGE = 5
_CRUISE_P: float = 3.0
_CRUISE_I: float = 0.03
_CRUISE_D: float = 0.6
_MAF_P: float = 4.0
_MAF_I: float = 0.01
_MAF_D: float = 0.1
_THROTTLE_P: float = 1.0
_THROTTLE_I: float = 0.01
_THROTTLE_D: float = 0.1

# Other globals
_RESET_PIN: int = 17


class Controller:
    """
    Class representing an engine controller.
    """

    # Class Variables
    MinSpeed: int = 0
    MaxSpeed: int = 100

    # Instance Variables
    __running: bool
    __accelerator_position: float
    __cruise_enabled: bool
    __cruise_pid: PID
    __cruise_target_speed: int
    __current_speed: int
    __dtc_list: List[DTC]
    __maf_value: float
    __maf_pid: PID
    __throttle_pid: PID
    __throttle_position: int

    # Constructor
    def __init__(self):
        global _CRUISE_P
        global _CRUISE_I
        global _CRUISE_D
        global _THROTTLE_P
        global _THROTTLE_I
        global _THROTTLE_D

        self.__running = False
        self.__accelerator_position = 0.00
        self.__cruise_enabled = False
        self.__cruise_pid = PID(_CRUISE_P, _CRUISE_I, _CRUISE_D, setpoint=0)
        self.__cruise_target_speed = 0
        self.__current_speed = 0
        self.__dtc_list = []
        self.__maf_value = 14.7
        self.__maf_pid = PID(_MAF_P, _MAF_I, _MAF_D, setpoint=14.7)
        self.__throttle_pid = PID(_THROTTLE_P, _THROTTLE_I, _THROTTLE_D, setpoint=0)
        self.__throttle_position = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)

    # Internal functions
    def __reset_throttle_body_board(self):
        # TODO: Increment reset count and process relevant DTC(s)
        print("----------------------\nRESETTING ARDUINO!\n----------------------")
        GPIO.output(17, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(17, GPIO.LOW)
        time.sleep(2.0)

    def __set_throttle_body(self, pos: int):
        # Restrict throttle body to 0 - 90 degrees
        if pos > 90:
            pos = 90
        elif pos < 0:
            pos = 0
        try:
            i2c.call_function(i2c.Function.FUNC_SET_SERVO, pos)
        except OSError:
            self.__reset_throttle_body_board()
            self.__set_throttle_body(pos)

    def __update_throttle(self):
        try:
            (response, result) = i2c.call_function(i2c.Function.FUNC_GET_SERVO)
        except OSError:
            self.__reset_throttle_body_board()
            self.get_throttle_body()
        else:
            if response:
                self.__throttle_position = result

    # Functions only used for testing, do not simulate real world behavior
    def __test__set_maf(self, maf: float):
        self.__maf_value = maf

    # Public Functions
    def cleanup(self):
        self.__running = False
        GPIO.cleanup()

    def get_accelerator_position(self) -> float:
        return self.__accelerator_position

    def set_accelerator_position(self, pos: float):
        # Sanity check, accelerator cannot go past 100% or be negative
        if pos > 1.00:
            pos = 1.00
        elif pos < 0.00:
            pos = 0.00
        self.__accelerator_position = pos

    def update_speed(self) -> int:
        # TODO: Read speed from something
        acceleration = int(12 * (self.get_throttle_body() / 90.00) - 2)
        self.__current_speed += acceleration
        if self.__current_speed < 0:
            self.__current_speed = 0
        return self.__current_speed

    def get_dtc_list(self) -> List[DTC]:
        return self.__dtc_list

    def get_cruise_control_status(self) -> bool:
        return self.__cruise_enabled

    def set_cruise_control_status(self, val: bool):
        self.__cruise_enabled = val

    def get_cruise_target_speed(self) -> int:
        return self.__cruise_target_speed

    def set_cruise_target_speed(self, speed: int):
        # Restrict cruise control to 0 - 100 mph
        if speed > self.MaxSpeed:
            speed = self.MaxSpeed
        elif speed < self.MinSpeed:
            speed = self.MinSpeed
        self.__cruise_target_speed = speed

    def get_throttle_body(self) -> int:
        return self.__throttle_position

    def get_maf_value(self) -> float:
        return self.__maf_value

    def simulate(self):
        global _ACCEL_DIFF_RANGE

        self.__running = True

        while self.__running:
            time.sleep(0.3)
            self.__update_throttle()
            if self.__cruise_enabled:
                print("Cruise enabled")
                speed = self.update_speed()
                print("ADJUSTING FOR SPEED...")
                self.__cruise_pid.setpoint = self.__cruise_target_speed
                output = int(self.__cruise_pid(speed))
                self.__set_throttle_body(output + self.__throttle_position)
            else:
                if (
                    self.__throttle_position
                    > self.__accelerator_position * 90 + _ACCEL_DIFF_RANGE
                    or self.__throttle_position
                    < self.__accelerator_position * 90 - _ACCEL_DIFF_RANGE
                ):
                    print("ADJUSTING FOR ACCEL...")
                    self.__throttle_pid.setpoint = self.__accelerator_position * 90
                    output = int(self.__throttle_pid(self.__throttle_position))
                    self.__set_throttle_body(output + self.__throttle_position)
                else:
                    print("ADJUSTING FOR MAF...")
                    cur_maf = self.get_maf_value()
                    output = int(self.__maf_pid(cur_maf))
                    self.__set_throttle_body(output + self.__throttle_position)
