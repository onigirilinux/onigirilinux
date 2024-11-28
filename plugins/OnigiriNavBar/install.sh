#!/bin/bash

# Create necessary directories
mkdir -p /usr/share/onigirilinux/plugins/navbar
mkdir -p /usr/local/bin
mkdir -p /etc/xdg/autostart

# Install dependencies
pacman -S --noconfirm python-cairo python-xlib libwnck3

# Copy files
cp stage_manager.py /usr/share/onigirilinux/plugins/navbar/
chmod +x /usr/share/onigirilinux/plugins/navbar/stage_manager.py

# Create launcher script
cat > /usr/local/bin/onigiri-stage-manager << EOL
#!/bin/bash
python3 /usr/share/onigirilinux/plugins/navbar/stage_manager.py
EOL
chmod +x /usr/local/bin/onigiri-stage-manager

# Create autostart entry
cat > /etc/xdg/autostart/com.onigirilinux.navbar.desktop << EOL
[Desktop Entry]
Name=Onigiri Stage Manager
Comment=3D window manager with gesture control
Exec=onigiri-stage-manager
Icon=preferences-system-windows
Terminal=false
Type=Application
Categories=GNOME;GTK;System;
X-GNOME-Autostart-enabled=true
EOL
