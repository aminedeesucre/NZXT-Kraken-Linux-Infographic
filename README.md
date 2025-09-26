# NZXT Kraken Z LCD Stats (Linux)

Display live system stats (CPU & GPU temps, optional RAM usage) on the LCD screen of NZXT Kraken Z-series coolers under Arch Linux.  
Tested on **Arch Linux** with NZXT Kraken Z280, Intel i7-13700K, and NVIDIA RTX 4080.  

The script generates a 320×320 PNG in RAM Memory (`/tmp`) every few seconds, then uploads it to the cooler LCD with `liquidctl`.  


## Prerequisites

### Arch Linux packages
```bash
sudo pacman -S python python-pip hidapi libusb python-pillow python-psutil ttf-dejavu lm_sensors liquidctl
````

### Python packages

```bash
yay -S python-nvidia-ml-py
```

---

## Usage

1. Clone or copy the script into `/usr/local/bin/nzxt_lcd.py`
2. Make it executable:

   ```bash
   sudo chmod +x /usr/local/bin/nzxt_lcd.py
   ```
3. Run manually for testing:

   ```bash
   sudo /usr/bin/python3 /usr/local/bin/nzxt_lcd.py
   ```

---

## Run as a systemd service for it to work in the background

Create `/etc/systemd/system/nzxt-lcd.service`:

```ini
[Unit]
Description=NZXT Kraken Z LCD updater
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/nzxt_lcd.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nzxt-lcd.service
```

The LCD will now show live stats automatically at boot.

---

## 🖼 Example

Sample LCD output layout:


![Temp](https://github.com/user-attachments/assets/7d94f5eb-779d-492c-be25-ad418feb9def)



---

## Notes

* `liquidctl` is required and must support your Kraken Z device.
* The script resets the LCD image every refresh; pump and fan are left at **firmware defaults** unless you override them separately.
* Works with NVIDIA GPUs; AMD support can be added by querying `rocm-smi`.

---
