# SPDX-FileCopyrightText: 2016 Radomir Dopieralski for Adafruit Industries
# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`pca9685`
================================================================================


MicroPython Driver for the PCA9685 PWM control IC. Its commonly used to control
servos, leds and motors.


* Author(s): Radomir Dopieralski, Scott Shawcroft, Jose D. Montoya


"""

import time
from micropython_pca9685.i2c_helpers import RegisterStruct, StructArray


class PWMChannel:
    """A single PCA9685 channel that matches the :py:class:`~pwmio.PWMOut` API.

    :param PCA9685 pca: The PCA9685 object
    :param int index: The index of the channel
    """

    def __init__(self, pca, index: int):
        self._pca = pca
        self._index = index

    @property
    def frequency(self) -> float:
        """The overall PWM frequency in Hertz (read-only).
        A PWMChannel's frequency cannot be set individually.
        All channels share a common frequency, set by PCA9685.frequency."""
        return self._pca.frequency

    @frequency.setter
    def frequency(self, _):
        raise NotImplementedError("frequency cannot be set on individual channels")

    @property
    def duty_cycle(self) -> int:
        """16 bit value that dictates how much of one cycle is high (1) versus low (0). 0xffff will
        always be high, 0 will always be low and 0x7fff will be half high and then half low.
        """
        pwm = self._pca.pwm_regs[self._index]

        if pwm[0] == 0x1000:
            return 0xFFFF
        if pwm[1] == 0x1000:
            return 0x0000
        return pwm[1] << 4

    @duty_cycle.setter
    def duty_cycle(self, value: int) -> None:
        if not 0 <= value <= 0xFFFF:
            raise ValueError(f"Out of range: value {value} not 0 <= value <= 65,535")

        if value == 0xFFFF:
            # Special case for "fully on":
            self._pca.pwm_regs[self._index] = (0x1000, 0)
        elif value < 0x0010:
            # Special case for "fully off":
            self._pca.pwm_regs[self._index] = (0, 0x1000)
        else:
            # Shift our value by four because the PCA9685 is only 12 bits but our value is 16
            value = value >> 4

            self._pca.pwm_regs[self._index] = (0, value)


class PCAChannels:
    """Lazily creates and caches channel objects as needed. Treat it like a sequence.

    :param PCA9685 pca: The PCA9685 object
    """

    def __init__(self, pca):
        self._pca = pca
        self._channels = [None] * len(self)

    def __len__(self) -> int:
        return 16

    def __getitem__(self, index: int) -> PWMChannel:
        if not self._channels[index]:
            self._channels[index] = PWMChannel(self._pca, index)
        return self._channels[index]


class PCA9685:
    """
    The internal reference clock is 25mhz but may vary slightly with environmental conditions and
    manufacturing variances. Providing a more precise ``reference_clock_speed`` can improve the
    accuracy of the frequency and duty_cycle computations. See the ``calibration.py`` example for
    how to derive this value by measuring the resulting pulse widths.

    """

    # Registers:
    mode1_reg = RegisterStruct(0x00, "<B")
    mode2_reg = RegisterStruct(0x01, "<B")
    prescale_reg = RegisterStruct(0xFE, "<B")
    pwm_regs = StructArray(0x06, "<HH", 16)

    def __init__(
        self,
        i2c,
        *,
        address: int = 0x40,
        reference_clock_speed: int = 25000000,
    ) -> None:
        self._i2c = i2c
        self._address = address

        self.channels = PCAChannels(self)
        """Sequence of 16 `PWMChannel` objects. One for each channel."""
        self.reference_clock_speed = reference_clock_speed
        """The reference clock speed in Hz."""
        self.reset()

    def reset(self) -> None:
        """Reset the chip."""
        self.mode1_reg = 0x00  # Mode1

    @property
    def frequency(self) -> float:
        """The overall PWM frequency in Hertz."""
        prescale_result = self.prescale_reg
        if prescale_result < 3:
            raise ValueError(
                "The device pre_scale register (0xFE) was not read or returned a value < 3"
            )
        return self.reference_clock_speed / 4096 / prescale_result

    @frequency.setter
    def frequency(self, freq: float) -> None:
        prescale = int(self.reference_clock_speed / 4096.0 / freq + 0.5)
        if prescale < 3:
            raise ValueError("PCA9685 cannot output at the given frequency")
        old_mode = self.mode1_reg  # Mode 1
        self.mode1_reg = (old_mode & 0x7F) | 0x10  # Mode 1, sleep
        self.prescale_reg = prescale  # Prescale
        self.mode1_reg = old_mode  # Mode 1
        time.sleep(0.005)
        # Mode 1, autoincrement on, fix to stop pca9685 from accepting commands at all addresses
        self.mode1_reg = old_mode | 0xA0

    def __enter__(self):
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        traceback,
    ):
        self.deinit()

    def deinit(self) -> None:
        """Stop using the pca9685."""
        self.reset()
