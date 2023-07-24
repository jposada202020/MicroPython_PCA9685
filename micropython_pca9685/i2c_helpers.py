# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`i2c_helpers`
================================================================================

I2C Communications helpers


* Author(s): Jose D. Montoya

Based on

* adafruit_register.i2c_struct. Author(s): Scott Shawcroft
* adafruit_register.i2c_bits.  Author(s): Scott Shawcroft
* adafruit_register.i2c_structarray.  Author(s): Scott Shawcroft

MIT License

Copyright (c) 2016 Adafruit Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
# pylint: disable=too-many-arguments
import struct


class CBits:
    """
    Changes bits from a byte register
    """

    def __init__(
        self,
        num_bits: int,
        register_address: int,
        start_bit: int,
        register_width=1,
        lsb_first=True,
    ) -> None:
        self.bit_mask = ((1 << num_bits) - 1) << start_bit
        self.register = register_address
        self.star_bit = start_bit
        self.lenght = register_width
        self.lsb_first = lsb_first

    def __get__(
        self,
        obj,
        objtype=None,
    ) -> int:
        mem_value = obj._i2c.readfrom_mem(obj._address, self.register, self.lenght)

        reg = 0
        order = range(len(mem_value) - 1, -1, -1)
        if not self.lsb_first:
            order = reversed(order)
        for i in order:
            reg = (reg << 8) | mem_value[i]

        reg = (reg & self.bit_mask) >> self.star_bit

        return reg

    def __set__(self, obj, value: int) -> None:
        memory_value = obj._i2c.readfrom_mem(obj._address, self.register, self.lenght)

        reg = 0
        order = range(len(memory_value) - 1, -1, -1)
        if not self.lsb_first:
            order = range(0, len(memory_value))
        for i in order:
            reg = (reg << 8) | memory_value[i]
        reg &= ~self.bit_mask

        value <<= self.star_bit
        reg |= value
        reg = reg.to_bytes(self.lenght, "big")

        obj._i2c.writeto_mem(obj._address, self.register, reg)


class RegisterStruct:
    """
    Register Struct
    """

    def __init__(self, register_address: int, form: str) -> None:
        self.format = form
        self.register = register_address
        self.lenght = struct.calcsize(form)

    def __get__(
        self,
        obj,
        objtype=None,
    ):
        if self.lenght <= 2:
            value = struct.unpack(
                self.format,
                memoryview(
                    obj._i2c.readfrom_mem(obj._address, self.register, self.lenght)
                ),
            )[0]
        else:
            value = struct.unpack(
                self.format,
                memoryview(
                    obj._i2c.readfrom_mem(obj._address, self.register, self.lenght)
                ),
            )
        return value

    def __set__(self, obj, value):
        mem_value = struct.pack(self.format, value)
        obj._i2c.writeto_mem(obj._address, self.register, mem_value)


class _BoundStructArray:
    """
    Array object that `StructArray` constructs on demand.

    :param object obj: The device object to bind to. It must have a `i2c` attribute
    :param int register_address: The register address to read the bit from
    :param str struct_format: The struct format string for each register element
    :param int count: Number of elements in the array
    """

    def __init__(
        self,
        obj,
        register_address,
        struct_format,
        count,
    ):
        self.format = struct_format
        self.first_register = register_address
        self.obj = obj
        self.count = count
        self.length = struct.calcsize(struct_format)

    def __getitem__(self, index):
        if not 0 <= index < self.count:
            raise IndexError()
        reg_to_get = self.first_register + self.length * index
        value = struct.unpack(
            self.format,
            memoryview(
                self.obj._i2c.readfrom_mem(self.obj._address, reg_to_get, self.length)
            ),
        )
        return value

    def __setitem__(self, index, value) -> None:
        reg_to_write = self.first_register + self.length * index
        mem_value = struct.pack(self.format, *value)
        self.obj._i2c.writeto_mem(self.obj._address, reg_to_write, mem_value)

    def __len__(self) -> int:
        return self.count


class StructArray:
    """
    Repeated array of structured registers that are readable and writeable.

    Based on the index, values are offset by the size of the structure.

    Values are tuples that map to the values in the defined struct.  See struct
    module documentation for struct format string and its possible value types.

    .. note:: This assumes the device addresses correspond to 8-bit bytes. This is not suitable for
      devices with registers of other widths such as 16-bit.

    :param int register_address: The register address to begin reading the array from
    :param str struct_format: The struct format string for this register.
    :param int count: Number of elements in the array
    """

    def __init__(self, register_address: int, struct_format: str, count: int) -> None:
        self.format = struct_format
        self.address = register_address
        self.count = count
        self.array_id = "_structarray{}".format(register_address)

    def __get__(
        self,
        obj,
        objtype=None,
    ) -> _BoundStructArray:
        # We actually can't handle the indexing ourselves due to
        # data descriptor limits. So, we return
        # an object that can instead. This object is bound to the
        # object passed in here by its
        # initializer and then cached on the object itself. That way its lifetime is tied to the
        # lifetime of the object itself.
        if not hasattr(obj, self.array_id):
            setattr(
                obj,
                self.array_id,
                _BoundStructArray(obj, self.address, self.format, self.count),
            )
        return getattr(obj, self.array_id)
