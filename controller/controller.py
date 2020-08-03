from typing import List
import i2c_comms as i2c
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
_ACCELERATOR_POS_RANGE: float = 0.05
_ACCELERATOR_POS_THROTTLE_INC: int = 5
_CRUISE_SPEED_RANGE: int = 2
_CRUISE_SPEED_THROTTLE_INC: int = 5
_MAF_SPEED_THROTTLE_INC: int = 3

class Controller:
    """
    Class representing an engine controller.
    """

    # Class Variables
    MinSpeed: int = 0
    MaxSpeed: int = 100

    # Instance Variables
    __accelerator_position: float
    __cruise_enabled: bool
    __cruise_target_speed: int
    __dtc_list: List[DTC]
    __maf_value: float

    # Constructor
    def __init__(self):
        self.__accelerator_position = 0.00
        self.__cruise_enabled = False
        self.__cruise_target_speed = 0
        self.__dtc_list = []
        self.__maf_value = 14.7

    # Internal functions
    def __set_throttle_body(self, pos: int):
        # Restrict throttle body to 0 - 90 degrees
        if pos > 90:
            pos = 90
        elif pos < 0:
            pos = 0
        i2c.call_function(i2c.Function.FUNC_SET_SERVO, pos)

    # Functions only used for testing, do not simulate real world behavior
    def __test__set_maf(self, maf: float):
        self.__maf_value = maf

    # Public Functions
    def get_accelerator_position(self) -> float:
        return self.__accelerator_position

    def set_accelerator_position(self, pos: float):
        # Sanity check, accelerator cannot go past 100% or be negative
        if pos > 1.00:
            pos = 1.00
        elif pos < 0.00:
            pos = 0.00
        self.__accelerator_position = pos

    def get_current_speed(self) -> int:
        # TODO: Read speed from something
        speed = 50
        return speed

    def get_dtc_list(self) -> List[DTC]:
        return self.__dtc_list

    def get_cruise_control_status(self) -> bool:
        return self.__cruise_enabled

    def toggle_cruise_control(self) -> bool:
        self.__cruise_enabled = not self.__cruise_enabled
        return self.__cruise_enabled

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
        (response, result) = i2c.call_function(i2c.Function.FUNC_GET_SERVO)
        if response:
            return result
        return None

    def get_maf_value(self) -> float:
        return self.__maf_value

    def simulate(self):
        global _ACCELERATOR_POS_RANGE
        global _ACCELERATOR_POS_THROTTLE_INC
        global _CRUISE_SPEED_RANGE
        global _CRUISE_SPEED_THROTTLE_INC
        global _MAF_SPEED_THROTTLE_INC
        
        # TODO: Possibly replace this with a file or some other external value to allow for external interrupt
        running: bool = True
        throttle_body_miss_comm_count: int = 0

        while running:
            time.sleep(0.2)
            if self.__cruise_enabled:
                print("Cruise enabled")
                speed = self.get_current_speed()
                print(f"Speed: {speed}, Target: {self.__cruise_target_speed}")
                if speed > self.__cruise_target_speed + _CRUISE_SPEED_RANGE or speed < self.__cruise_target_speed - _CRUISE_SPEED_RANGE:
                    throttle_adjust: int
                    if speed < self.__cruise_target_speed:
                        # TODO: Use control method
                        throttle_adjust = _CRUISE_SPEED_THROTTLE_INC
                    else:
                        throttle_adjust = -1 * _CRUISE_SPEED_THROTTLE_INC
                    cur_throttle =  self.get_throttle_body()
                    if cur_throttle == None:
                        # TODO: More granular DTCs
                        throttle_body_miss_comm_count += 1
                        if throttle_body_miss_comm_count > 5:
                            print(f"Setting DTC #1: Loss of comms with throttle body")
                            self.__dtc_list.append(DTC(1, "Loss of comms with throttle body"))
                        continue
                    throttle_body_miss_comm_count = 0
                    print(f"Adjusting throttle to {cur_throttle + throttle_adjust}")
                    self.__set_throttle_body(cur_throttle + throttle_adjust)
            else:
                cur_throttle = self.get_throttle_body()
                if cur_throttle == None:
                    # TODO: More granular DTCs
                    throttle_body_miss_comm_count += 1
                    if throttle_body_miss_comm_count > 5:
                        print(f"Setting DTC #1: Loss of comms with throttle body")
                        self.__dtc_list.append(DTC(1, "Loss of comms with throttle body"))
                    continue
                throttle_body_miss_comm_count = 0
                cur_throttle_rel = cur_throttle / 90.00
                print(f"Throttle %: {cur_throttle_rel * 100.00}, Accelerator %: {self.__accelerator_position * 100.00}")
                if cur_throttle_rel > self.__accelerator_position + _ACCELERATOR_POS_RANGE or cur_throttle_rel < self.__accelerator_position - _ACCELERATOR_POS_RANGE:
                    throttle_adjust: int
                    if cur_throttle_rel < self.__accelerator_position:
                        # TODO: Use control method
                        throttle_adjust = _ACCELERATOR_POS_THROTTLE_INC
                    else:
                        throttle_adjust = -1 * _ACCELERATOR_POS_THROTTLE_INC
                    print(f"Adjusting throttle to {cur_throttle + throttle_adjust}")
                    self.__set_throttle_body(cur_throttle + throttle_adjust)
                else:
                    maf = self.get_maf_value()
                    print(f"MAF: {maf}")
                    if maf != 14.7:
                        throttle_adjust: int
                        if maf < 14.7:
                            # TODO: Use control method
                            throttle_adjust = _MAF_SPEED_THROTTLE_INC
                        else:
                            throttle_adjust = -1 * _MAF_SPEED_THROTTLE_INC
                        print(f"Adjusting throttle to {cur_throttle + throttle_adjust}")
                        self.__set_throttle_body(cur_throttle + throttle_adjust)
