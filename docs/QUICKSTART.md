# SnapStash — 3-Step Quickstart

Get your private photo cloud running in under 2 minutes.

---

## What You Need

- 🟢 **Raspberry Pi 5** (4GB or 8GB RAM)
- 🟢 **MicroSD card** (16GB+)
- 🟢 **USB Hard Drive** (any size — this is where your photos live)
- 🟢 **Ethernet cable** (recommended) or WiFi
- 🟢 **Phone** (iOS or Android)

---

## Step 1: 📥 Flash

1. Download the latest **SnapStash image** from the [Releases page](../../releases).
2. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
3. Open Pi Imager → Choose OS → **Use Custom** → Select the SnapStash `.img.xz` file.
4. Choose your SD card as the target.
5. Click **Write** and wait for it to finish.

---

## Step 2: 🔌 Plug

1. Insert the flashed SD card into your Raspberry Pi 5.
2. Plug in your USB hard drive to any USB port.
3. Connect an Ethernet cable to your router (or it will create a **SnapStash-Setup** WiFi network).
4. Plug in the power cable.
5. Wait ~60 seconds for the Pi to boot.

---

## Step 3: 📱 Scan

1. On your phone, open your camera and point it at the QR code displayed at:
   ```
   http://snapstash.local
   ```
   Or open your browser and navigate to that URL directly.

2. Tap **Install App** when prompted to add SnapStash to your home screen.

3. Open the app and tap **Start Backup**.

4. Select your photos and videos.

5. Tap **🚀 Start Backup** — SnapStash will:
   - ✅ Hash your files to skip duplicates
   - ✅ Upload in chunks (safe for large 4K videos)
   - ✅ Keep your screen on during the sync
   - ✅ Show real-time progress and ETA

---

## 🎉 You're Done!

Your photos are now safely stored on **your** hard drive. No cloud. No subscription. Fully private.

---

## Troubleshooting

### Can't find `snapstash.local`?
- Make sure your phone is on the **same network** as the Pi.
- Try the Pi's IP address directly (check your router's admin page).
- If using WiFi mode, connect to the `SnapStash-Setup` network first.

### USB drive not detected?
- Try a different USB port on the Pi.
- Make sure the drive is formatted as ext4, NTFS, or exFAT.
- Check the drive works on a computer first.

### Upload seems stuck?
- Make sure your phone screen is on (the app uses Wake Lock to prevent sleep).
- Check that the Pi hasn't run out of disk space.
- Try backing up in smaller batches.
