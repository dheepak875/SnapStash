#!/bin/bash
# Install Docker CE on Raspberry Pi OS
curl -fsSL https://get.docker.com | sh
usermod -aG docker pi
systemctl enable docker
