#!/usr/bin/env python3
# ColourSensorMatrix — TCS34725 grid via PCA9548A mux (no GUI)
# Returns RGB as [R,G,B] 8-bit integers per channel

import json, time
from pathlib import Path
import numpy as np
import board, busio
import adafruit_tcs34725


class PCA9548AChannel:
    """Lightweight I2C channel wrapper for PCA9548A mux."""
    def __init__(self, i2c, mux_address=0x70, channel=0):
        assert 0 <= channel <= 7
        self._i2c = i2c
        self._addr = mux_address
        self._mask = 1 << channel

    def try_lock(self):
        return self._i2c.try_lock()

    def unlock(self):
        self._i2c.unlock()

    def _select(self):
        self._i2c.writeto(self._addr, bytes([self._mask]))

    def writeto(self, addr, buf, *, start=0, end=None):
        self._select()
        return self._i2c.writeto(addr, buf, start=start, end=end)

    def readfrom_into(self, addr, buf, *, start=0, end=None):
        self._select()
        return self._i2c.readfrom_into(addr, buf, start=start, end=end)

    def writeto_then_readfrom(self, addr, bo, bi, *, out_start=0, out_end=None, in_start=0, in_end=None):
        self._select()
        return self._i2c.writeto_then_readfrom(
            addr, bo, bi,
            out_start=out_start, out_end=out_end,
            in_start=in_start, in_end=in_end
        )


class ColourSensorMatrix:
    """Multi-sensor color reader using PCA9548A mux + TCS34725 sensors."""

    MUX_ADDR = 0x70
    TARGET_ADDR = 0x29
    CAL_PATH = Path.home() / ".tcs34725_cal_mux.json"

    IT_VALUES   = [2.4, 24, 50, 101, 154]
    GAIN_VALUES = [1, 4, 16]
    C_TARGET_MIN, C_TARGET_MAX, C_CLIP = 12000, 45000, 60000

    def __init__(self, mux_addr=0x70, target_addr=0x29):
        self.mux_addr = mux_addr
        self.target_addr = target_addr
        self.base_i2c = busio.I2C(board.SCL, board.SDA)
        self.channels = self._detect_channels()
        if not self.channels:
            raise RuntimeError("No TCS34725 sensors found on mux channels.")

        self.sensors = {
            ch: adafruit_tcs34725.TCS34725(PCA9548AChannel(self.base_i2c, mux_addr, ch))
            for ch in self.channels
        }
        for s in self.sensors.values():
            s.integration_time = 154
            s.gain = 16

        self.cal_db = self._load_calibration()

    # --------------------------------------------------
    # Initialization / Calibration
    # --------------------------------------------------
    def _detect_channels(self):
        found = []
        for ch in range(8):
            while not self.base_i2c.try_lock(): pass
            try:
                self.base_i2c.writeto(self.mux_addr, bytes([1 << ch]))
            finally:
                self.base_i2c.unlock()

            while not self.base_i2c.try_lock(): pass
            try:
                addrs = self.base_i2c.scan()
            finally:
                self.base_i2c.unlock()

            if self.target_addr in addrs:
                found.append(ch)
        return found

    def _load_calibration(self):
        if not self.CAL_PATH.exists():
            raise FileNotFoundError(f"Calibration file not found: {self.CAL_PATH}")
        try:
            cal = json.loads(self.CAL_PATH.read_text())
        except Exception as e:
            raise RuntimeError(f"Failed to parse calibration JSON at {self.CAL_PATH}: {e}")
        missing = [str(ch) for ch in self.channels if str(ch) not in cal]
        if missing:
            raise KeyError(f"Calibration missing for channel(s): {', '.join(missing)} in {self.CAL_PATH}")
        return cal

    def get_cal(self, ch):
        key = str(ch)
        if key not in self.cal_db:
            raise KeyError(f"No calibration found for channel {ch} in {self.CAL_PATH}")
        return self.cal_db[key]

    # --------------------------------------------------
    # Color math helpers
    # --------------------------------------------------
    @staticmethod
    def _clamp8(x): return int(max(0, min(255, round(x))))
    @staticmethod
    def _normalize(r, g, b, c): return np.zeros(3) if c <= 0 else np.array([r/c, g/c, b/c], float)
    @staticmethod
    def _apply_wb(v, wb): return v * np.array(wb, float)
    @staticmethod
    def _to_8bit(v): return [ColourSensorMatrix._clamp8(x * 255.0) for x in np.clip(v, 0, 1)]

    @staticmethod
    def _rgb_saturation(v, sat):
        m = np.array([[0.2126,0.7152,0.0722],
                      [-0.2126,0.2848,-0.0722],
                      [-0.2126,-0.7152,0.9278]])
        yuv = m @ v
        yuv[1:] *= sat
        return np.linalg.inv(m) @ yuv

    @staticmethod
    def _linear_to_srgb(v, gamma):
        v = np.clip(v, 0, 1)
        return np.power(v, 1.0 / float(gamma))

    def _sensor_to_srgb(self, v, cal):
        v = np.array(v, float)
        M = np.asarray(cal["ccm"], float) if cal.get("ccm_enabled", True) else np.eye(3)
        mapped = M @ v
        mapped = self._rgb_saturation(mapped, cal["saturation"])
        m = mapped.max()
        if m > 0:
            mapped = mapped / m
        return self._linear_to_srgb(mapped, cal["gamma"])

    # --------------------------------------------------
    # Auto exposure
    # --------------------------------------------------
    def _idx(self, seq, val):
        try:
            return seq.index(val)
        except ValueError:
            diffs = [abs(x - val) for x in seq]
            return int(np.argmin(diffs))

    def _auto_expose(self, sensor, c):
        it_i = self._idx(self.IT_VALUES, sensor.integration_time)
        g_i = self._idx(self.GAIN_VALUES, sensor.gain)
        changed = False

        if c >= self.C_CLIP or (c > self.C_TARGET_MAX and (it_i > 0 or g_i > 0)):
            if g_i > 0:
                g_i -= 1
            elif it_i > 0:
                it_i -= 1
            changed = True
        elif c < self.C_TARGET_MIN and (it_i < len(self.IT_VALUES) - 1 or g_i < len(self.GAIN_VALUES) - 1):
            if g_i < len(self.GAIN_VALUES) - 1:
                g_i += 1
            elif it_i < len(self.IT_VALUES) - 1:
                it_i += 1
            changed = True

        if changed:
            sensor.gain = self.GAIN_VALUES[g_i]
            sensor.integration_time = self.IT_VALUES[it_i]
        return changed

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def get_color(self, ch):
        """Return [R, G, B] as 8-bit ints for a given channel."""
        if ch not in self.sensors:
            raise ValueError(f"Channel {ch} not found (available: {self.channels})")

        s = self.sensors[ch]
        r, g, b, c = s.color_raw
        if self._auto_expose(s, c):
            time.sleep(0.01)
            r, g, b, c = s.color_raw

        cal = self.get_cal(ch)
        v = self._normalize(r, g, b, c)
        v = self._apply_wb(v, cal["wb"])
        sr = self._sensor_to_srgb(v, cal)
        return self._to_8bit(sr)

    def get_all_colors(self):
        """Return {channel: [R,G,B]} for all detected sensors."""
        return {ch: self.get_color(ch) for ch in self.channels}
