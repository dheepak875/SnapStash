#!/usr/bin/env python3
"""
SnapStash WiFi Hotspot Fallback
If no internet is detected after boot, creates a WiFi access point
so users can connect directly to the Pi.
"""

import subprocess
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WiFi] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("wifi-hotspot")

SSID = "SnapStash-Setup"
PASSPHRASE = ""  # Open network for easy setup
INTERFACE = "wlan0"
AP_IP = "192.168.4.1"
DHCP_RANGE = "192.168.4.10,192.168.4.50,24h"
CONNECTIVITY_TIMEOUT = 30  # seconds to wait for internet


HOSTAPD_CONF = f"""
interface={INTERFACE}
driver=nl80211
ssid={SSID}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
"""

DNSMASQ_CONF = f"""
interface={INTERFACE}
dhcp-range={DHCP_RANGE}
address=/#/{AP_IP}
"""


def check_internet():
    """Check for internet connectivity."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "3", "8.8.8.8"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def check_ethernet():
    """Check if Ethernet is connected."""
    try:
        result = subprocess.run(
            ["ip", "link", "show", "eth0"],
            capture_output=True,
            text=True,
        )
        return "state UP" in result.stdout
    except Exception:
        return False


def start_hotspot():
    """Start WiFi hotspot mode."""
    log.info(f"🔥 Starting WiFi hotspot: SSID='{SSID}'")

    # Configure static IP for wlan0
    subprocess.run(
        ["ip", "addr", "flush", "dev", INTERFACE],
        capture_output=True,
    )
    subprocess.run(
        ["ip", "addr", "add", f"{AP_IP}/24", "dev", INTERFACE],
        capture_output=True,
    )
    subprocess.run(
        ["ip", "link", "set", INTERFACE, "up"],
        capture_output=True,
    )

    # Write hostapd config
    with open("/tmp/snapstash_hostapd.conf", "w") as f:
        f.write(HOSTAPD_CONF)

    # Write dnsmasq config
    with open("/tmp/snapstash_dnsmasq.conf", "w") as f:
        f.write(DNSMASQ_CONF)

    # Stop existing services
    subprocess.run(["systemctl", "stop", "wpa_supplicant"], capture_output=True)

    # Start hostapd
    subprocess.Popen(
        ["hostapd", "/tmp/snapstash_hostapd.conf"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Start dnsmasq (DNS/DHCP)
    subprocess.Popen(
        ["dnsmasq", "-C", "/tmp/snapstash_dnsmasq.conf", "--no-daemon"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    log.info(f"✅ Hotspot active at {AP_IP}")
    log.info(f"   Connect to WiFi network: '{SSID}'")
    log.info(f"   Then open: http://{AP_IP}")


def stop_hotspot():
    """Stop WiFi hotspot and return to client mode."""
    log.info("Stopping hotspot...")
    subprocess.run(["pkill", "hostapd"], capture_output=True)
    subprocess.run(["pkill", "-f", "snapstash_dnsmasq"], capture_output=True)
    subprocess.run(["ip", "addr", "flush", "dev", INTERFACE], capture_output=True)
    subprocess.run(["systemctl", "start", "wpa_supplicant"], capture_output=True)
    log.info("Reverted to WiFi client mode")


def main():
    """Main loop — check connectivity and switch modes as needed."""
    log.info("🌐 WiFi hotspot service started")
    log.info(f"Waiting {CONNECTIVITY_TIMEOUT}s for network...")

    # Wait for network on boot
    deadline = time.time() + CONNECTIVITY_TIMEOUT
    while time.time() < deadline:
        if check_internet() or check_ethernet():
            log.info("✅ Network connectivity detected — hotspot not needed")
            break
        time.sleep(3)
    else:
        log.warning("❌ No network connectivity detected")
        start_hotspot()

    # Monitor connectivity and switch modes
    hotspot_active = not (check_internet() or check_ethernet())
    try:
        while True:
            time.sleep(30)
            has_network = check_internet() or check_ethernet()

            if has_network and hotspot_active:
                log.info("Network restored — switching to client mode")
                stop_hotspot()
                hotspot_active = False

            elif not has_network and not hotspot_active:
                log.warning("Network lost — activating hotspot")
                start_hotspot()
                hotspot_active = True

    except KeyboardInterrupt:
        if hotspot_active:
            stop_hotspot()
        log.info("WiFi service stopped")


if __name__ == "__main__":
    main()
