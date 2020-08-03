"""Module for simplifying I2C communication using smbus2"""

from smbus2 import SMBus, i2c_msg
import struct, sys

# Private globals
__SMBUS_ACTIVE: bool = False
__SMBUS_OBJ: SMBus = None


def init_bus(num: int) -> bool:
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if __SMBUS_ACTIVE:
        print(
            "Bus is already active, please close the bus before re-initializing",
            file=sys.stderr,
        )
        return False

    __SMBUS_OBJ = SMBus(num)
    __SMBUS_ACTIVE = True
    return True


def close_bus():
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    __SMBUS_OBJ.close()
    __SMBUS_ACTIVE = False


def write_bytes(address: int, data: bytes):
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    msg: i2c_msg = i2c_msg.write(address, data)
    __SMBUS_OBJ.i2c_rdwr(msg)


def write_int(
    address: int,
    value: int,
    int_sz: int = 32,
    signed: bool = True,
    byte_order: str = "little",
):
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    if int_sz < 0:
        print("Integer size must be positive", file=sys.stderr)
        return
    elif int_sz > 64:
        print("Max integer size is 64-bit", file=sys.stderr)
        return
    elif int_sz not in [8, 16, 32, 64]:
        print("Irregular integer size, rounding up...")
        if int_sz < 8:
            int_sz = 8
        elif int_sz < 16:
            int_sz = 16
        elif int_sz < 32:
            int_sz = 32
        elif int_sz < 64:
            int_sz = 64

    msg: i2c_msg = i2c_msg.write(
        address, value.to_bytes(int_sz // 8, byteorder=byte_order, signed=signed)
    )
    __SMBUS_OBJ.i2c_rdwr(msg)


def write_float(address: int, value: float, double_precision: bool = False):
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    data: bytes
    if double_precision:
        data = struct.pack("d", value)
    else:
        data = struct.pack("f", value)

    msg: i2c_msg = i2c_msg.write(address, data)
    __SMBUS_OBJ.i2c_rdwr(msg)


def write_int8(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 8, byte_order=byte_order)


def write_int16(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 16, byte_order=byte_order)


def write_int32(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 32, byte_order=byte_order)


def write_int64(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 64, byte_order=byte_order)


def write_uint8(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 8, signed=False, byte_order=byte_order)


def write_uint16(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 16, signed=False, byte_order=byte_order)


def write_uint32(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 32, signed=False, byte_order=byte_order)


def write_uint64(address: int, value: int, byte_order: str = "little"):
    write_int(address, value, 64, signed=False, byte_order=byte_order)


def read_bytes(address: int, num_bytes: int) -> bytes:
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    msg: i2c_msg = i2c_msg.read(address, num_bytes)
    __SMBUS_OBJ.i2c_rdwr(msg)
    return bytes(msg)


def read_int(
    address: int, int_sz: int = 32, signed: bool = True, byte_order: str = "little"
) -> int:
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    if int_sz < 0:
        print("Integer size must be positive", file=sys.stderr)
        return
    elif int_sz > 64:
        print("Max integer size is 64-bit", file=sys.stderr)
        return
    elif int_sz not in [8, 16, 32, 64]:
        print("Irregular integer size, rounding up...")
        if int_sz < 8:
            int_sz = 8
        elif int_sz < 16:
            int_sz = 16
        elif int_sz < 32:
            int_sz = 32
        elif int_sz < 64:
            int_sz = 64

    msg: i2c_msg = i2c_msg.read(address, int_sz // 8)
    __SMBUS_OBJ.i2c_rdwr(msg)
    return int.from_bytes(bytes(msg), byteorder=byte_order, signed=signed)


def read_float(address: int, double_precision: bool = False) -> float:
    global __SMBUS_ACTIVE
    global __SMBUS_OBJ

    if not __SMBUS_ACTIVE:
        print("Bus is not active, please initialize the bus first", file=sys.stderr)
        return

    sz: int
    fmt: str
    if double_precision:
        sz = 8
        fmt = "d"
    else:
        sz = 4
        fmt = "f"

    msg = i2c_msg.read(address, sz)
    __SMBUS_OBJ.i2c_rdwr(msg)
    [x] = struct.unpack(fmt, bytes(msg))
    return x


def read_int8(address: int, byte_order: str = "little") -> int:
    return read_int(address, 8, byte_order=byte_order)


def read_int16(address: int, byte_order: str = "little") -> int:
    return read_int(address, 16, byte_order=byte_order)


def read_int32(address: int, byte_order: str = "little") -> int:
    return read_int(address, 32, byte_order=byte_order)


def read_int64(address: int, byte_order: str = "little") -> int:
    return read_int(address, 64, byte_order=byte_order)


def read_uint8(address: int, byte_order: str = "little") -> int:
    return read_int(address, 8, signed=False, byte_order=byte_order)


def read_uint16(address: int, byte_order: str = "little") -> int:
    return read_int(address, 16, signed=False, byte_order=byte_order)


def read_uint32(address: int, byte_order: str = "little") -> int:
    return read_int(address, 32, signed=False, byte_order=byte_order)


def read_uint64(address: int, byte_order: str = "little") -> int:
    return read_int(address, 64, signed=False, byte_order=byte_order)
