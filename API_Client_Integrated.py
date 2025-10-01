#!/usr/bin/env python3
# TCS34725 grid viewer (Raspberry Pi 5) via PCA9548A mux
# - Auto‑detect sensors on channels 0..7 (0x29)
# - One swatch tile per connected sensor, live updates
# - Per-channel Auto-Exposure (AE), Gray-world WB, optional CCM, Gamma, Saturation
# - Cal saved in ~/.tcs34725_cal_mux.json
#
# Keys (operate on the *selected* tile):
#   0..7 = select channel/tile
#   w    = gray-world white balance (show white card)
#   c    = CCM calibrator (follow terminal prompts)
#   t    = toggle CCM on/off
#   s/S  = saturation -/+ (current channel)
#   g/G  = gamma -/+ (current channel)
#   r    = reset cal for current channel
#   q    = quit

import json
import sys
import time
import math
import threading
import asyncio
import tkinter as tk
from pathlib import Path

import numpy as np
import board
import busio
import adafruit_tcs34725

from DeviceApiClient.ApiClient import ApiClient
from StandardLibrary.PythonTypes import ColourAlert


# --------- PCA9548A wrapper ---------
class PCA9548AChannel:
    def __init__(self, i2c, mux_address=0x70, channel=0):
        assert 0 <= channel <= 7
        self._i2c = i2c
        self._addr = mux_address
        self._mask = 1 << channel
    def try_lock(self): return self._i2c.try_lock()
    def unlock(self): self._i2c.unlock()
    def deinit(self):
        try: self._i2c.deinit()
        except AttributeError: pass
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
        return self._i2c.writeto_then_readfrom(addr, bo, bi,
                                               out_start=out_start, out_end=out_end,
                                               in_start=in_start, in_end=in_end)

# --------- I2C & sensor detection ---------
MUX_ADDR = 0x70
TARGET_ADDR = 0x29

base_i2c = busio.I2C(board.SCL, board.SDA)

def detect_channels(base_bus, mux_addr=0x70, target=0x29):
    found = []
    for ch in range(8):
        # select channel
        while not base_bus.try_lock():
            pass
        try:
            base_bus.writeto(mux_addr, bytes([1 << ch]))
        finally:
            base_bus.unlock()

        # scan downstream
        while not base_bus.try_lock():
            pass
        try:
            addrs = base_bus.scan()
        finally:
            base_bus.unlock()

        if target in addrs:
            found.append(ch)
    return found

CHANNELS = detect_channels(base_i2c, mux_addr=MUX_ADDR, target=TARGET_ADDR)
if not CHANNELS:
    raise RuntimeError("No TCS34725 found on any mux channel.")

# Build sensor objects
sensors = {}
for ch in CHANNELS:
    ch_bus = PCA9548AChannel(base_i2c, mux_address=MUX_ADDR, channel=ch)
    s = adafruit_tcs34725.TCS34725(ch_bus)
    # start bright so AE settles quickly
    s.integration_time = 154  # ms (2.4, 24, 50, 101, 154, 614)
    s.gain = 16               # 1, 4, 16, 60
    sensors[ch] = s

# Exposure thresholds / AE
IT_VALUES   = [2.4, 24, 50, 101, 154]
GAIN_VALUES = [1, 4, 16]
C_TARGET_MIN, C_TARGET_MAX, C_CLIP = 12000, 45000, 60000

def _idx(seq, val):
    try:
        return seq.index(val)
    except ValueError:
        diffs = [abs(x - val) for x in seq]
        return int(np.argmin(diffs))

def auto_expose(sensor, c):
    it_i = _idx(IT_VALUES, sensor.integration_time)
    g_i  = _idx(GAIN_VALUES, sensor.gain)
    # too bright / clipping
    if c >= C_CLIP or (c > C_TARGET_MAX and (it_i > 0 or g_i > 0)):
        if g_i > 0:
            g_i -= 1
        elif it_i > 0:
            it_i -= 1
        sensor.gain = GAIN_VALUES[g_i]
        sensor.integration_time = IT_VALUES[it_i]
        return True
    # too dim
    if c < C_TARGET_MIN and (it_i < len(IT_VALUES)-1 or g_i < len(GAIN_VALUES)-1):
        if g_i < len(GAIN_VALUES)-1:
            g_i += 1
        elif it_i < len(IT_VALUES)-1:
            it_i += 1
        sensor.gain = GAIN_VALUES[g_i]
        sensor.integration_time = IT_VALUES[it_i]
        return True
    return False

# Per-channel calibration storage
CAL_PATH = Path.home() / ".tcs34725_cal_mux.json"

def _default_cal():
    return {
        "wb": [1.0, 1.0, 1.0],
        "ccm": np.eye(3).tolist(),
        "gamma": 2.20,
        "saturation": 1.00,
        "ccm_enabled": True
    }

if CAL_PATH.exists():
    try:
        CAL_DB = json.loads(CAL_PATH.read_text())
    except Exception:
        CAL_DB = {}
else:
    CAL_DB = {}

for ch in CHANNELS:
    CAL_DB.setdefault(str(ch), _default_cal())

def cal_get(ch):
    return CAL_DB[str(ch)]

def cal_save():
    out = {}
    for k, v in CAL_DB.items():
        vv = dict(v)
        vv["ccm"] = np.asarray(vv["ccm"], dtype=float).tolist()
        out[k] = vv
    CAL_PATH.write_text(json.dumps(out, indent=2))

# Color processing
def clamp8(x):
    return int(max(0, min(255, round(x))))

def normalize_by_clear(r, g, b, c):
    if c <= 0:
        return np.zeros(3)
    return np.array([r/c, g/c, b/c], dtype=float)

def apply_wb(v, wb):
    return v * np.array(wb, dtype=float)

def rgb_saturation(v, sat):
    m = np.array([[0.2126, 0.7152, 0.0722],
                  [-0.2126, 0.2848, -0.0722],
                  [-0.2126, -0.7152, 0.9278]])
    yuv = m @ v
    yuv[1:] *= sat
    invm = np.linalg.inv(m)
    return invm @ yuv

def linear_to_srgb(v, gamma):
    v = np.clip(v, 0, 1)
    return np.power(v, 1.0 / float(gamma))

def srgb_to_linear(v, gamma):
    v = np.clip(v, 0, 1)
    return np.power(v, float(gamma))

def to_8bit(v):
    return tuple(clamp8(x * 255.0) for x in np.clip(v, 0, 1))

def sensor_to_srgb(v, cal):
    v = np.array(v, dtype=float)
    M = np.asarray(cal["ccm"], dtype=float) if cal.get("ccm_enabled", True) else np.eye(3)
    mapped = M @ v
    mapped = rgb_saturation(mapped, cal["saturation"])
    m = mapped.max()
    if m > 0:
        mapped = mapped / m
    return linear_to_srgb(mapped, cal["gamma"])

# WB & CCM calibration
PATCHES = [
    ("White", (1, 1, 1)),
    ("Red", (1, 0, 0)),
    ("Green", (0, 1, 0)),
    ("Blue", (0, 0, 1)),
    ("Cyan", (0, 1, 1)),
    ("Magenta", (1, 0, 1)),
    ("Yellow", (1, 1, 0)),
]

def gray_world_wb(sensor, ch, samples=10, settle=0.2):
    acc = np.zeros(3)
    for _ in range(samples):
        r, g, b, c = sensor.color_raw
        acc += [r, g, b]
        time.sleep(settle / samples)
    r, g, b = acc / samples
    mean = max(1.0, (r + g + b) / 3.0)
    wb = [mean / max(r, 1.0), mean / max(g, 1.0), mean / max(b, 1.0)]
    wb = [float(min(max(w, 0.25), 4.0)) for w in wb]
    cal_get(ch)["wb"] = wb
    cal_save()
    return wb

def calibrate_ccm(sensor, ch, gamma=None, samples=12, settle=0.3):
    if gamma is None:
        gamma = cal_get(ch)["gamma"]
    print(f"\n== CCM Calibration (channel {ch}) ==")
    print("Show each patch FULL‑SCREEN on a monitor/phone at max brightness under SAME lighting.")
    print("Order: White, Red, Green, Blue, Cyan, Magenta, Yellow.")
    print("For each color: put sensor ~1–2 cm on screen, avoid moiré; press ENTER to capture…\n")
    cal = cal_get(ch)
    sens, refs = [], []
    old_ccm, old_enabled = cal["ccm"], cal.get("ccm_enabled", True)
    # Temporarily disable CCM
    cal["ccm"] = np.eye(3).tolist()
    cal["ccm_enabled"] = False
    try:
        for name, srgb in PATCHES:
            input(f"[Ch{ch} {name}] press ENTER when ready...")
            acc = np.zeros(4)
            for _ in range(samples):
                r, g, b, c = sensor.color_raw
                acc += [r, g, b, c]
                time.sleep(settle / samples)
            r, g, b, c = acc / samples
            v = normalize_by_clear(r, g, b, c)
            v = apply_wb(v, cal["wb"])
            sens.append(v)
            refs.append(np.array(srgb_to_linear(np.array(srgb), gamma), dtype=float))
            print(f"  sensor={v}, ref_linear={refs[-1]}")
        S = np.stack(sens, axis=0)
        R = np.stack(refs, axis=0)
        Sp = np.linalg.pinv(S)
        M_t = Sp @ R
        M = M_t.T
        cal["ccm"] = M.tolist()
        cal["ccm_enabled"] = True
        cal_save()
        print("CCM saved.")
    finally:
        # restore old enabled state if needed
        cal["ccm_enabled"] = cal.get("ccm_enabled", True) if "ccm" in cal else old_enabled

# --------- API client & async loop setup ---------
api_client = ApiClient(base_url="placeholder") 

# Start asyncio loop in a background thread
loop = asyncio.new_event_loop()
def _loop_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=_loop_thread, daemon=True).start()

# Tk UI (grid of tiles)
REFRESH_MS = 200
root = tk.Tk()
root.title("TCS34725 Mux Grid Viewer")

# compute grid layout
N = len(CHANNELS)
cols = int(math.ceil(math.sqrt(N)))
rows = int(math.ceil(N / cols))

tile_frames = {}
tiles = {}  # ch -> dict of widgets/state
selected_ch = CHANNELS[0]

def build_tile(ch, row, col):
    f = tk.Frame(root, bd=2, relief="groove", padx=8, pady=8)
    f.grid(row=row, column=col, padx=8, pady=8, sticky="nwes")
    root.grid_columnconfigure(col, weight=1)
    root.grid_rowconfigure(row, weight=1)

    title = tk.Label(f, text=f"Channel {ch}", font=("Arial", 12, "bold"))
    title.grid(row=0, column=0, sticky="w")

    sw = tk.Canvas(f, width=220, height=110, highlightthickness=0)
    sw.grid(row=1, column=0, pady=(6,4))
    rect = sw.create_rectangle(0,0,220,110, fill="#000000", outline="")

    rgb = tk.Label(f, text="RGB: --, --, --", font=("Arial", 12))
    hexx = tk.Label(f, text="#------", font=("Arial", 12))
    raw = tk.Label(f, text="Raw: R -- G -- B -- C --", font=("Arial", 10))
    exp = tk.Label(f, text="IT -- ms  Gain --", font=("Arial", 10))
    fx  = tk.Label(f, text="", font=("Arial", 10))
    stat= tk.Label(f, text="Status: --", font=("Arial", 10))

    rgb.grid(row=2, column=0, sticky="w")
    hexx.grid(row=3, column=0, sticky="w")
    raw.grid(row=4, column=0, sticky="w", pady=(4,0))
    exp.grid(row=5, column=0, sticky="w")
    fx.grid(row=6, column=0, sticky="w")
    stat.grid(row=7, column=0, sticky="w")

    tile_frames[ch] = f
    tiles[ch] = {
        "sw": sw, "rect": rect, "rgb": rgb, "hex": hexx,
        "raw": raw, "exp": exp, "fx": fx, "stat": stat, "title": title
    }

for idx, ch in enumerate(CHANNELS):
    r = idx // cols
    c = idx % cols
    build_tile(ch, r, c)

def highlight_selection():
    for ch, f in tile_frames.items():
        if ch == selected_ch:
            f.config(highlightbackground="deepskyblue", highlightthickness=3)
        else:
            f.config(highlightthickness=0)

def update_tile(ch):
    s = sensors[ch]
    try:
        r, g, b, c = s.color_raw
        if auto_expose(s, c):
            time.sleep(0.01)
            r, g, b, c = s.color_raw

        cal = cal_get(ch)
        v = normalize_by_clear(r, g, b, c)
        v = apply_wb(v, cal["wb"])
        
        # Convert normalized linear rgb [0-1] to 0-255 8bit integers
        linear_rgb_255 = [clamp8(x * 255.0) for x in v]

        # Send to API client using receiveColour coroutine
        try:
            colour_alert = ColourAlert(
                channel=ch,
                linear_rgb=linear_rgb_255
            )
            asyncio.run_coroutine_threadsafe(
                api_client.receiveColour(colour_alert),
                loop
            )
        except Exception as ex:
            print(f"[API] Error sending data for channel {ch}: {ex}")

        # ... rest of update_tile code unchanged ...
        
        sr = sensor_to_srgb(v, cal)
        R8, G8, B8 = to_8bit(sr)
        hex_str = f"#{R8:02X}{G8:02X}{B8:02X}"

        t = tiles[ch]
        t["sw"].itemconfig(t["rect"], fill=hex_str)
        t["rgb"].config(text=f"RGB: {R8}, {G8}, {B8}")
        t["hex"].config(text=hex_str)
        t["raw"].config(text=f"Raw: R {int(r)}  G {int(g)}  B {int(b)}  C {int(c)}")
        t["exp"].config(text=f"IT {s.integration_time:.1f} ms   Gain {s.gain}x")
        t["fx"].config(text=f"CCM:{'on' if cal.get('ccm_enabled', True) else 'off'}  γ:{cal['gamma']:.2f}  sat:{cal['saturation']:.2f}")

        if c >= C_CLIP:
            t["stat"].config(text="Status: CLIPPING", fg="red")
        elif c < C_TARGET_MIN:
            t["stat"].config(text="Status: Dim", fg="orange")
        elif c > C_TARGET_MAX:
            t["stat"].config(text="Status: Bright", fg="orange")
        else:
            t["stat"].config(text="Status: OK", fg="green")

    except Exception as e:
        tiles[ch]["stat"].config(text=f"Error: {e}", fg="red")


def tick():
    for ch in CHANNELS:
        update_tile(ch)
    root.after(REFRESH_MS, tick)

def select_channel(n):
    global selected_ch
    if n in CHANNELS:
        selected_ch = n
        highlight_selection()

def on_key(e):
    global selected_ch
    k = e.keysym
    lk = k.lower()

    # select tile 0..7
    if lk in tuple("01234567"):
        select_channel(int(lk))
        return

    cal = cal_get(selected_ch)
    s = sensors[selected_ch]

    if lk == 'w':
        tiles[selected_ch]["stat"].config(text="Calibrating WB… show WHITE", fg="blue")
        root.update_idletasks()
        gray_world_wb(s, selected_ch)
        tiles[selected_ch]["stat"].config(text="WB set", fg="green")

    elif lk == 'c':
        root.withdraw()
        try:
            calibrate_ccm(s, selected_ch, gamma=cal["gamma"])
            tiles[selected_ch]["stat"].config(text="CCM saved", fg="green")
        finally:
            root.deiconify()

    elif lk == 't':
        cal["ccm_enabled"] = not cal.get("ccm_enabled", True)
        cal_save()

    elif lk == 's':
        cal["saturation"] = max(0.10, round(cal["saturation"] - 0.05, 2))
        cal_save()
    elif k == 'S':
        cal["saturation"] = min(3.00, round(cal["saturation"] + 0.05, 2))
        cal_save()

    elif lk == 'g':
        cal["gamma"] = max(1.40, round(cal["gamma"] - 0.05, 2))
        cal_save()
    elif k == 'G':
        cal["gamma"] = min(2.80, round(cal["gamma"] + 0.05, 2))
        cal_save()

    elif lk == 'r':
        CAL_DB[str(selected_ch)] = _default_cal()
        cal_save()
        tiles[selected_ch]["stat"].config(text="Reset", fg="blue")

    elif lk == 'q':
        root.destroy()
        # Stop asyncio loop gracefully
        loop.call_soon_threadsafe(loop.stop)
        sys.exit(0)

root.bind("<Key>", on_key)
highlight_selection()
root.after(REFRESH_MS, tick)
root.mainloop()
