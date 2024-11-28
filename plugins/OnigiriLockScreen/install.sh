#!/bin/bash

# Create necessary directories
mkdir -p /usr/share/onigirilinux/plugins/lockscreen
mkdir -p /usr/local/bin
mkdir -p /usr/share/applications

# Install required fonts
pacman -S --noconfirm ttf-roboto ttf-jetbrains-mono ttf-comic-neue ttf-playfair-display

# Copy files
cp lockscreen_customizer.py /usr/share/onigirilinux/plugins/lockscreen/
chmod +x /usr/share/onigirilinux/plugins/lockscreen/lockscreen_customizer.py

# Create launcher script
cat > /usr/local/bin/onigiri-lockscreen << EOL
#!/bin/bash
python3 /usr/share/onigirilinux/plugins/lockscreen/lockscreen_customizer.py
EOL
chmod +x /usr/local/bin/onigiri-lockscreen

# Create desktop entry
cat > /usr/share/applications/com.onigirilinux.lockscreen.desktop << EOL
[Desktop Entry]
Name=Onigiri LockScreen
Comment=Customize your lock screen
Exec=onigiri-lockscreen
Icon=preferences-system-time
Terminal=false
Type=Application
Categories=GNOME;GTK;Settings;
EOL
