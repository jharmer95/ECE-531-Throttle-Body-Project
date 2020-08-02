#!./.venv/bin/python3
from typing import Dict, List
import i2c_comms as i2c
import simple_i2c as si2c
import struct, sys, time

si2c.init_bus(1)


    
si2c.close_bus()
