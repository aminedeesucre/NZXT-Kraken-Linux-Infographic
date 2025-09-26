#!/usr/bin/env python3
"""
NZXT Kraken Z280 LCD updater
Shows only CPU and GPU temps, side by side, like NZXT CAM does.
"""

import time, subprocess, psutil
from PIL import Image, ImageDraw, ImageFont
import pynvml

# Path where we generate the temporary PNG (lives in RAM at /tmp)
PNG_PATH = "/tmp/nzxt_lcd.png"

# Fonts to use (installed via ttf-dejavu on Arch)
FONT_BOLD = "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/TTF/DejaVuSans.ttf"

# Match string for liquidctl (so we target the right device)
DEVICE = "kraken"

# ──────────────────────────────────────────────
# NVIDIA GPU: initialize NVML (NVIDIA Management Library)
# ──────────────────────────────────────────────
pynvml.nvmlInit()
gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # 0 = first GPU (your RTX 4080)


# ──────────────────────────────────────────────
# Get CPU temperature from psutil/lm-sensors
# ──────────────────────────────────────────────
def get_cpu_temp():
    temps = psutil.sensors_temperatures()
    for _, entries in temps.items():
        for e in entries:
            # Look for labels that typically indicate CPU package temperature
            if "Package" in e.label or "Tctl" in e.label or "cpu" in e.label.lower():
                return int(e.current)
    return None


# ──────────────────────────────────────────────
# Get GPU temperature via NVIDIA NVML
# ──────────────────────────────────────────────
def get_gpu_temp():
    return int(pynvml.nvmlDeviceGetTemperature(
        gpu_handle, pynvml.NVML_TEMPERATURE_GPU))


# ──────────────────────────────────────────────
# Render a 320×320 PNG with CPU/GPU temps
# ──────────────────────────────────────────────
def render_png(cpu_temp, gpu_temp):
    # Create a blank 320x320 black background
    img = Image.new("RGB", (320, 320), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fonts for big numbers, labels, and title
    f_big   = ImageFont.truetype(FONT_BOLD, 80)
    f_label = ImageFont.truetype(FONT_REG, 28)
    f_title = ImageFont.truetype(FONT_BOLD, 32)

    # Title "NZXT" at the top, roughly centered
    draw.text((120, 20), "NZXT", font=f_title, fill=(255,255,255))

    # CPU section on the left
    draw.text((40, 120), f"{cpu_temp}°", font=f_big, fill=(3,169,252))
    draw.text((80, 220), "CPU", font=f_label, fill=(3,169,252))

    # GPU section on the right
    draw.text((190, 120), f"{gpu_temp}°", font=f_big, fill=(252,186,3))
    draw.text((230, 220), "GPU", font=f_label, fill=(252,186,3))

    # Save image to /tmp (RAM) so we can upload it
    img.save(PNG_PATH, "PNG")


# ──────────────────────────────────────────────
# Push the generated PNG to the LCD using liquidctl
# ──────────────────────────────────────────────
def push_to_lcd():
    # Try static image mode first
    result = subprocess.run(
        ["liquidctl", "--match", DEVICE,
         "set", "lcd", "screen", "static", PNG_PATH],
        stderr=subprocess.PIPE
    )
    # If that fails (different firmware), try gif mode
    if result.returncode != 0:
        subprocess.run(
            ["liquidctl", "--match", DEVICE,
             "set", "lcd", "screen", "gif", PNG_PATH],
            check=False
        )


# ──────────────────────────────────────────────
# Main loop: read temps → render PNG → push LCD
# ──────────────────────────────────────────────
def main():
    # Initialize Kraken pump/fan/LCD
    subprocess.run(["liquidctl", "initialize", "all"], check=False)

    while True:
        # Gather stats
        cpu_temp = get_cpu_temp()
        gpu_temp = get_gpu_temp()

        # Draw new PNG with current values
        render_png(cpu_temp, gpu_temp)

        # Upload it to the LCD
        push_to_lcd()

        # Wait 5 seconds before refreshing again
        time.sleep(2)


# ──────────────────────────────────────────────
# Run until stopped (Ctrl+C)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
