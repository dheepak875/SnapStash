#!/usr/bin/env python3
"""
SnapStash mDNS Broadcaster
Registers the SnapStash HTTP service via Zeroconf so the Pi
is discoverable at snapstash.local on the local network.
"""

import socket
import sys
import time
import signal
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [mDNS] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("mdns")

SERVICE_TYPE = "_http._tcp.local."
SERVICE_NAME = "SnapStash._http._tcp.local."
SERVICE_PORT = 80  # Nginx port
HOSTNAME = "snapstash"


def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def set_avahi_hostname():
    """Set the avahi hostname to 'snapstash' for .local resolution."""
    try:
        subprocess.run(
            ["hostnamectl", "set-hostname", HOSTNAME],
            capture_output=True,
            text=True,
        )
        log.info(f"Set hostname to '{HOSTNAME}'")
    except Exception as e:
        log.warning(f"Could not set hostname: {e}")


def run_broadcaster():
    """Register and maintain the mDNS service."""
    try:
        from zeroconf import ServiceInfo, Zeroconf
    except ImportError:
        log.error("zeroconf not installed. Install with: pip install zeroconf")
        sys.exit(1)

    # Set hostname
    set_avahi_hostname()

    local_ip = get_local_ip()
    log.info(f"Local IP: {local_ip}")

    info = ServiceInfo(
        SERVICE_TYPE,
        SERVICE_NAME,
        addresses=[socket.inet_aton(local_ip)],
        port=SERVICE_PORT,
        properties={
            "path": "/",
            "version": "1.0.0",
            "app": "snapstash",
        },
        server=f"{HOSTNAME}.local.",
    )

    zeroconf = Zeroconf()

    def shutdown(signum=None, frame=None):
        log.info("Unregistering mDNS service...")
        zeroconf.unregister_service(info)
        zeroconf.close()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log.info(f"📡 Registering mDNS service: {SERVICE_NAME}")
    log.info(f"   → http://{HOSTNAME}.local:{SERVICE_PORT}")
    zeroconf.register_service(info)
    log.info("✅ mDNS service registered — broadcasting on local network")

    # Keep running
    try:
        while True:
            time.sleep(60)
            # Re-check IP in case it changed
            new_ip = get_local_ip()
            if new_ip != local_ip:
                log.info(f"IP changed: {local_ip} → {new_ip}")
                local_ip = new_ip
                zeroconf.unregister_service(info)
                info = ServiceInfo(
                    SERVICE_TYPE,
                    SERVICE_NAME,
                    addresses=[socket.inet_aton(local_ip)],
                    port=SERVICE_PORT,
                    properties={"path": "/", "version": "1.0.0", "app": "snapstash"},
                    server=f"{HOSTNAME}.local.",
                )
                zeroconf.register_service(info)
                log.info("Re-registered with new IP")
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    run_broadcaster()
