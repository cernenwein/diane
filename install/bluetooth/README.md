# Bluetooth Scripts for Diane - JLab GO Air Sport

## Files
- `pair_device.sh`: Scans, pairs, trusts, and connects to the earbuds.
- `auto_connect.sh`: Reconnects to known earbuds on boot.
- `bluetooth-auto-connect.service`: Systemd unit to run auto-connect on startup.

## Usage

### 1. Pair Your Earbuds
```bash
./pair_device.sh
```

### 2. Set Up Auto-Connect
```bash
sudo cp bluetooth-auto-connect.service /etc/systemd/system/
sudo systemctl enable bluetooth-auto-connect
sudo systemctl start bluetooth-auto-connect
```

### 3. Diane Voice Commands (Suggested)
- “Diane, reconnect my earbuds” → runs `auto_connect.sh`
- “Diane, pair my JLab earbuds” → runs `pair_device.sh`
