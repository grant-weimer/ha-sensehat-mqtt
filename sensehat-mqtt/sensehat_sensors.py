"""
Read Sense HAT environmental sensors (HTS221, LPS25H) via I2C without sense-hat/RTIMULib.
Uses smbus2 so we can run on Alpine and avoid broken RTIMULib builds.
"""
import os
import struct
import time

# Sense HAT uses I2C bus 1, HTS221 at 0x5F, LPS25H at 0x5C (SDO to GND)
I2C_BUS = 1
HTS221_ADDR = 0x5F
LPS25H_ADDR = 0x5C


def _read_s16(bus, addr, register):
    """Read 16-bit signed from two consecutive registers (LSB first)."""
    data = bus.read_i2c_block_data(addr, register, 2)
    return struct.unpack("<h", bytes(data))[0]


class SenseHATSensors:
    """Read temperature, humidity, and pressure from Sense HAT via I2C (HTS221 + LPS25H)."""

    def __init__(self, bus_num=I2C_BUS):
        i2c_dev = f"/dev/i2c-{bus_num}"
        if not os.path.exists(i2c_dev):
            raise FileNotFoundError(
                f"{i2c_dev} not found. Enable I2C on the host (e.g. HassOS I2C Configurator add-on) "
                "and ensure this addon has the device configured (devices: /dev/i2c-1)."
            )
        import smbus2
        self._bus = smbus2.SMBus(bus_num)
        self._hts221_cal = None
        self._init_hts221()
        self._init_lps25h()

    def _init_hts221(self):
        # Power on, 1 Hz output, BDU (block data update)
        self._bus.write_byte_data(HTS221_ADDR, 0x20, 0x87)
        time.sleep(0.05)
        # Calibration: HTS221 uses 10-bit T0_degC_x8, T1_degC_x8 (LSB in 0x32/0x33, 2 MSB in 0x35)
        H0_rH_x2 = self._bus.read_byte_data(HTS221_ADDR, 0x30)
        H1_rH_x2 = self._bus.read_byte_data(HTS221_ADDR, 0x31)
        t0_lsb = self._bus.read_byte_data(HTS221_ADDR, 0x32)
        t1_lsb = self._bus.read_byte_data(HTS221_ADDR, 0x33)
        t01_msb = self._bus.read_byte_data(HTS221_ADDR, 0x35)
        T0_degC_x8 = ((t01_msb & 0x03) << 8) | t0_lsb
        T1_degC_x8 = (((t01_msb >> 2) & 0x03) << 8) | t1_lsb
        T0_degC = T0_degC_x8 / 8.0
        T1_degC = T1_degC_x8 / 8.0
        H0_T0_OUT = _read_s16(self._bus, HTS221_ADDR, 0x36)
        H1_T0_OUT = _read_s16(self._bus, HTS221_ADDR, 0x3A)
        T0_OUT = _read_s16(self._bus, HTS221_ADDR, 0x3C)
        T1_OUT = _read_s16(self._bus, HTS221_ADDR, 0x3E)
        self._hts221_cal = {
            "H0_rH": H0_rH_x2 / 2.0,
            "H1_rH": H1_rH_x2 / 2.0,
            "T0_degC": T0_degC,
            "T1_degC": T1_degC,
            "H0_T0_OUT": H0_T0_OUT,
            "H1_T0_OUT": H1_T0_OUT,
            "T0_OUT": T0_OUT,
            "T1_OUT": T1_OUT,
        }

    def _init_lps25h(self):
        # Power on, 25 Hz internal update
        self._bus.write_byte_data(LPS25H_ADDR, 0x20, 0x90)
        time.sleep(0.02)

    def _hts221_temp(self):
        """Temperature in °C from HTS221 (humidity sensor)."""
        T_OUT = _read_s16(self._bus, HTS221_ADDR, 0x2A)
        c = self._hts221_cal
        denom = c["T1_OUT"] - c["T0_OUT"]
        if denom == 0:
            return (c["T0_degC"] + c["T1_degC"]) / 2.0
        return c["T0_degC"] + (T_OUT - c["T0_OUT"]) * (c["T1_degC"] - c["T0_degC"]) / denom

    def get_temperature_from_humidity(self):
        return self._hts221_temp()

    def get_temperature_from_pressure(self):
        """Temperature in °C from LPS25H (pressure sensor)."""
        raw = _read_s16(self._bus, LPS25H_ADDR, 0x2B)
        return 42.5 + raw / 480.0

    def get_humidity(self):
        """Relative humidity in % from HTS221."""
        H_T_OUT = _read_s16(self._bus, HTS221_ADDR, 0x28)
        c = self._hts221_cal
        denom = c["H1_T0_OUT"] - c["H0_T0_OUT"]
        if denom == 0:
            return (c["H0_rH"] + c["H1_rH"]) / 2.0
        return c["H0_rH"] + (H_T_OUT - c["H0_T0_OUT"]) * (c["H1_rH"] - c["H0_rH"]) / denom

    def get_pressure(self):
        """Pressure in hPa (mbar) from LPS25H."""
        data = self._bus.read_i2c_block_data(LPS25H_ADDR, 0x28, 3)
        raw = data[0] | (data[1] << 8) | (data[2] << 16)
        if raw & 0x800000:
            raw -= 0x1000000
        return raw / 4096.0

    def close(self):
        self._bus.close()
