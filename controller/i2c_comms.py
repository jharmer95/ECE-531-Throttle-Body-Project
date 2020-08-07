"""Module for communicating with the Arduino via I2c and a custom function buffer"""

__author__ = "Jackson Harmer"
__copyright__ = "Copyright (c) 2020 Jackson Harmer. All rights reserved."
__license__ = "MIT"
__version__ = "0.1"

from enum import IntEnum, unique
from typing import Any, Dict, List, Tuple
from simple_i2c import read_bytes, write_bytes
import struct, sys

# Globals
ADDR = 0x08  # bus address


@unique
class Function(IntEnum):
    FUNC_GET_SERVO = 1
    FUNC_SET_SERVO = 2


@unique
class ErrorCode(IntEnum):
    ERROR_NONE = 0
    ERROR_GENERIC = -1


class Buffer:
    cmd: int
    params: Dict[str, List]
    union_type: str

    def __init__(self, cmd):
        self.cmd = cmd
        self.params = {
            "ints": [0, 0, 0, 0, 0, 0, 0],
            "floats": [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            "string": "",
        }
        self.union_type = "int"

    def pack(self) -> bytes:
        if self.union_type == "void":
            data = struct.pack("<b", self.cmd)
            while len(data) < 28:
                data += bytes([0])
            return data
        elif self.union_type == "int":
            return struct.pack("<biiiiiii", self.cmd, *self.params["ints"][0:7])
        elif self.union_type == "uint":
            return struct.pack("<bIIIIIII", self.cmd, *self.params["ints"][0:7])
        elif self.union_type == "float":
            return struct.pack("<bfffffff", self.cmd, *self.params["floats"][0:7])
        elif self.union_type == "string":
            data = struct.pack(
                "<bs", self.cmd, self.params["string"].encode("utf-8")[0:27]
            )
            while len(data) < 28:
                data += bytes([0])
            return data
        else:
            return bytes()

    @classmethod
    def unpack(cls, data: bytes, u_type: str):
        if u_type == "void":
            [cmd] = struct.unpack("<b", data[0:1])
            inst = cls(cmd)
            inst.union_type = "void"
            return inst
        elif u_type == "int":
            [cmd, i1, i2, i3, i4, i5, i6, i7] = struct.unpack("<biiiiiii", data)
            inst = cls(cmd)
            inst.params["ints"] = [i1, i2, i3, i4, i5, i6, i7]
            inst.union_type = "int"
            return inst
        elif u_type == "uint":
            [cmd, i1, i2, i3, i4, i5, i6, i7] = struct.unpack("<bIIIIIII", data)
            inst = cls(cmd)
            inst.params["ints"] = [i1, i2, i3, i4, i5, i6, i7]
            inst.union_type = "uint"
            return inst
        elif u_type == "float":
            [cmd, i1, i2, i3, i4, i5, i6, i7] = struct.unpack("<bfffffff", data)
            inst = cls(cmd)
            inst.params["floats"] = [i1, i2, i3, i4, i5, i6, i7]
            inst.union_type = "float"
            return inst
        elif u_type == "string":
            [cmd] = struct.unpack("<b", data[0:1])
            s = data[1:28].decode("utf-8")
            inst = cls(cmd)
            inst.params["string"] = s
            inst.union_type = "string"
            return inst


def call_function(function: Function, *args) -> Tuple[bool, Any]:
    global ADDR

    mesg_buf = Buffer(function)
    return_type: str = "int"

    if function == Function.FUNC_GET_SERVO:
        pass
    elif function == Function.FUNC_SET_SERVO:
        mesg_buf.params["ints"][0] = args[0]
        mesg_buf.union_type = "int"
        return_type = "void"

    write_bytes(ADDR, mesg_buf.pack())

    response = read_bytes(ADDR, 29)
    mesg_buf = Buffer.unpack(response, return_type)

    if mesg_buf.cmd != ErrorCode.ERROR_NONE:
        mesg_buf = Buffer.unpack(response, "string")
        print(f"Error {mesg_buf.cmd}: {mesg_buf.params['string']}")
        return (False, mesg_buf.cmd)

    if return_type == "void":
        return (True, None)
    elif return_type == "int" or return_type == "uint":
        return (True, mesg_buf.params["ints"][0])
    elif return_type == "float":
        return (True, mesg_buf.params["floats"][0])
