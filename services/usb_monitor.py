#!/usr/bin/env python3
"""
SnapStash USB Auto-Mount Daemon
Monitors USB ports for block devices and automatically mounts HDDs.
Runs as a systemd service with root privileges.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [USB-Monitor] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("usb-monitor")

MOUNT_POINT = "/data/snapstash"
SENTINEL_FILE = "SNAPSTASH_READY"
FOLDER_STRUCTURE = ["photos", "temp"]


def create_folder_structure(base_path: str):
    """Create the required SnapStash folder structure on the drive."""
    for folder in FOLDER_STRUCTURE:
        path = Path(base_path) / folder
        path.mkdir(parents=True, exist_ok=True)
        log.info(f"  → Created {path}")

    # Write sentinel file
    sentinel = Path(base_path) / SENTINEL_FILE
    sentinel.write_text(f"SnapStash storage initialized at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.info(f"  → Wrote sentinel: {sentinel}")


def mount_device(device_node: str):
    """Mount a USB device to the SnapStash mount point."""
    mount_path = Path(MOUNT_POINT)
    mount_path.mkdir(parents=True, exist_ok=True)

    # Check if already mounted
    result = subprocess.run(["findmnt", "-n", str(mount_path)], capture_output=True, text=True)
    if result.returncode == 0:
        log.warning(f"Mount point {MOUNT_POINT} already in use, skipping")
        return False

    # Attempt mount
    log.info(f"Mounting {device_node} → {MOUNT_POINT}")
    result = subprocess.run(
        ["mount", "-o", "defaults,noatime", device_node, str(mount_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.error(f"Mount failed: {result.stderr.strip()}")
        return False

    log.info(f"✅ Mounted successfully")
    create_folder_structure(MOUNT_POINT)
    return True


def unmount_device():
    """Gracefully unmount the SnapStash storage."""
    mount_path = Path(MOUNT_POINT)
    if not mount_path.exists():
        return

    log.info(f"Unmounting {MOUNT_POINT}...")
    result = subprocess.run(
        ["umount", str(mount_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        log.info("✅ Unmounted successfully")
    else:
        log.warning(f"Unmount issue: {result.stderr.strip()}")


def monitor_usb():
    """Monitor USB devices using pyudev."""
    try:
        import pyudev
    except ImportError:
        log.error("pyudev not installed. Install with: pip install pyudev")
        log.info("Falling back to polling mode...")
        monitor_usb_polling()
        return

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block")

    log.info("🔌 USB monitor started — waiting for devices...")

    # Check for already-connected devices on startup
    for device in context.list_devices(subsystem="block", DEVTYPE="partition"):
        if device.get("ID_BUS") == "usb":
            log.info(f"Found existing USB device: {device.device_node}")
            mount_device(device.device_node)
            break

    # Watch for new devices
    for device in iter(monitor.poll, None):
        if device.device_type != "partition":
            continue

        if device.action == "add":
            log.info(f"🔌 USB device added: {device.device_node}")
            time.sleep(2)  # Wait for device to settle
            mount_device(device.device_node)

        elif device.action == "remove":
            log.info(f"🔌 USB device removed: {device.device_node}")
            unmount_device()


def monitor_usb_polling():
    """Fallback polling-based USB monitoring (no pyudev)."""
    log.info("🔌 USB monitor (polling mode) started...")
    was_mounted = False

    while True:
        # Check if any USB block device exists
        try:
            result = subprocess.run(
                ["lsblk", "-o", "NAME,TRAN,TYPE", "-n", "-l"],
                capture_output=True,
                text=True,
            )
            usb_partitions = [
                line.split()[0]
                for line in result.stdout.strip().split("\n")
                if "usb" in line and "part" in line
            ]
        except Exception:
            usb_partitions = []

        if usb_partitions and not was_mounted:
            device = f"/dev/{usb_partitions[0]}"
            log.info(f"Detected USB partition: {device}")
            if mount_device(device):
                was_mounted = True

        elif not usb_partitions and was_mounted:
            log.info("USB device removed")
            unmount_device()
            was_mounted = False

        time.sleep(5)


if __name__ == "__main__":
    try:
        monitor_usb()
    except KeyboardInterrupt:
        log.info("Shutting down USB monitor")
        sys.exit(0)
