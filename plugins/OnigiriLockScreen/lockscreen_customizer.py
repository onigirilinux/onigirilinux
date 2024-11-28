#!/usr/bin/env python3
import gi
import os
import json
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio

FONTS = {
    "Default": "Cantarell",
    "Modern": "Roboto",
    "Elegant": "Playfair Display",
    "Tech": "JetBrains Mono",
    "Fun": "Comic Neue"
}

class LockScreenCustomizer(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.onigirilinux.lockscreen')
        self.connect('activate', self.on_activate)
        
    def on_activate(self, app):
        self.win = Adw.ApplicationWindow(application=app)
        self.win.set_default_size(400, 300)
        self.win.set_title("LockScreen Customizer")

        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)

        # Content
        content = Adw.PreferencesPage()
        
        # Font selection group
        font_group = Adw.PreferencesGroup()
        font_group.set_title("Lock Screen Font")
        font_group.set_description("Choose a font for your lock screen")
        
        # Create font selection combo box
        combo_row = Adw.ComboRow()
        combo_row.set_title("Select Font")
        combo_row.set_model(Gtk.StringList.new(list(FONTS.keys())))
        combo_row.connect('notify::selected', self.on_font_changed)
        
        font_group.add(combo_row)
        
        # Preview group
        preview_group = Adw.PreferencesGroup()
        preview_group.set_title("Preview")
        
        self.preview_label = Gtk.Label()
        self.preview_label.set_markup("<span size='xx-large'>12:00</span>")
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        preview_box.append(self.preview_label)
        
        preview_group.add(preview_box)
        
        content.add(font_group)
        content.add(preview_group)
        
        main_box.append(content)
        
        self.win.set_content(main_box)
        self.win.present()
    
    def on_font_changed(self, combo_row, *args):
        selected = combo_row.get_selected()
        font_name = list(FONTS.values())[selected]
        
        # Update preview
        self.preview_label.set_markup(f"<span size='xx-large' font='{font_name}'>12:00</span>")
        
        # Update GDM settings
        self._update_gdm_settings(font_name)
    
    def _update_gdm_settings(self, font_name):
        # Create custom CSS for GDM
        css_content = f"""
#clock-label {{
    font-family: "{font_name}";
}}
"""
        
        # Write to GDM custom CSS file
        css_path = Path("/etc/gdm/custom.css")
        try:
            with open(css_path, "w") as f:
                f.write(css_content)
            
            # Restart GDM to apply changes
            os.system("systemctl restart gdm")
        except Exception as e:
            print(f"Error updating GDM settings: {str(e)}")

def main():
    app = LockScreenCustomizer()
    app.run(None)

if __name__ == "__main__":
    main()
