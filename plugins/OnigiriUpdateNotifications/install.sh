#!/bin/bash

# Create necessary directories
mkdir -p /usr/share/onigirilinux/plugins/update-notifications
mkdir -p /etc/systemd/user

# Copy files
cp update_checker.py /usr/share/onigirilinux/plugins/update-notifications/
chmod +x /usr/share/onigirilinux/plugins/update-notifications/update_checker.py

# Create systemd user service
cat > /etc/systemd/user/onigiri-update-notifications.service << EOL
[Unit]
Description=OnigiriLinux Update Notifications
After=network-online.target

[Service]
ExecStart=/usr/share/onigirilinux/plugins/update-notifications/update_checker.py
Restart=always

[Install]
WantedBy=default.target
EOL

# Enable and start service for all users
systemctl --global enable onigiri-update-notifications.service
systemctl --global start onigiri-update-notifications.service
