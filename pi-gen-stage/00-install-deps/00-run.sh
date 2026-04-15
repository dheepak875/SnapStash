#!/bin/bash -e
# pi-gen stage: Install SnapStash dependencies

# Install Docker
install -m 755 files/install-docker.sh "${ROOTFS_DIR}/tmp/"
on_chroot << EOF
bash /tmp/install-docker.sh
rm /tmp/install-docker.sh
EOF

# Install system packages
on_chroot << EOF
apt-get update
apt-get install -y --no-install-recommends \
    avahi-daemon \
    hostapd \
    dnsmasq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    usbutils
EOF
