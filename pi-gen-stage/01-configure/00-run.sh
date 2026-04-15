#!/bin/bash -e
# pi-gen stage: Configure SnapStash services

# Copy SnapStash application files
install -d "${ROOTFS_DIR}/opt/snapstash"

# Copy source code (built Docker images will be pulled/built on first boot)
cp -r "${STAGE_DIR}/files/snapstash/"* "${ROOTFS_DIR}/opt/snapstash/"

# Install systemd services
install -m 644 "${STAGE_DIR}/files/snapstash/services/snapstash-usb.service" \
    "${ROOTFS_DIR}/etc/systemd/system/"
install -m 644 "${STAGE_DIR}/files/snapstash/services/snapstash-mdns.service" \
    "${ROOTFS_DIR}/etc/systemd/system/"
install -m 644 "${STAGE_DIR}/files/snapstash/services/snapstash-wifi.service" \
    "${ROOTFS_DIR}/etc/systemd/system/"

# Install first-boot script
install -m 755 "${STAGE_DIR}/files/first-boot.sh" "${ROOTFS_DIR}/opt/snapstash/"

# Enable services
on_chroot << EOF
# Set hostname
hostnamectl set-hostname snapstash

# Enable systemd services
systemctl enable snapstash-usb.service
systemctl enable snapstash-mdns.service
systemctl enable snapstash-wifi.service
systemctl enable avahi-daemon

# Install Python dependencies for services
pip3 install --break-system-packages zeroconf pyudev

# Create data directory
mkdir -p /data/snapstash

# Set up first-boot docker compose
cat > /etc/systemd/system/snapstash-firstboot.service << UNIT
[Unit]
Description=SnapStash First Boot Setup
After=docker.service network-online.target
Wants=network-online.target
ConditionPathExists=!/opt/snapstash/.initialized

[Service]
Type=oneshot
ExecStart=/opt/snapstash/first-boot.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
UNIT
systemctl enable snapstash-firstboot.service
EOF
