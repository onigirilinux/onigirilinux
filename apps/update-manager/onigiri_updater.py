import gi
import requests
import os
import threading
import json
from pathlib import Path
import tempfile
import subprocess

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf

class OnigiriUpdater(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.onigirilinux.updater')
        self.connect('activate', self.on_activate)
        self.version_info = None
        self.current_version = "1.0.0"  # Questo dovrebbe essere letto da un file di configurazione
        
    def on_activate(self, app):
        self.win = Adw.ApplicationWindow(application=app)
        self.win.set_default_size(800, 600)
        self.win.set_title("Onigiri Update Manager")

        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header bar
        header = Adw.HeaderBar()
        refresh_button = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_button.connect("clicked", self.check_updates)
        header.pack_start(refresh_button)
        main_box.append(header)

        # Content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)

        # Banner
        self.banner_image = Gtk.Picture()
        self.banner_image.set_size_request(760, 250)
        content_box.append(self.banner_image)

        # Version info
        self.version_label = Gtk.Label()
        self.version_label.set_markup("<big><b>Current version:</b> " + self.current_version + "</big>")
        content_box.append(self.version_label)

        # Changelog
        changelog_frame = Adw.PreferencesGroup()
        changelog_frame.set_title("Changelog")
        
        self.changelog_text = Gtk.TextView()
        self.changelog_text.set_editable(False)
        self.changelog_text.set_wrap_mode(Gtk.WrapMode.WORD)
        self.changelog_buffer = self.changelog_text.get_buffer()
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(200)
        scrolled.set_child(self.changelog_text)
        changelog_frame.add(scrolled)
        
        content_box.append(changelog_frame)

        # Update button
        self.update_button = Gtk.Button(label="Install Update")
        self.update_button.get_style_context().add_class("suggested-action")
        self.update_button.connect("clicked", self.install_update)
        self.update_button.set_sensitive(False)
        content_box.append(self.update_button)

        main_box.append(content_box)
        self.win.set_content(main_box)
        self.win.present()

        # Check for updates on startup
        self.check_updates(None)

    def check_updates(self, button):
        def check():
            try:
                # Controlla l'ultima release su GitHub
                response = requests.get("https://api.github.com/repos/onigirilinux/ota_server/releases/latest")
                self.version_info = response.json()
                
                # Scarica il banner
                banner_url = None
                changelog_content = ""
                
                for asset in self.version_info["assets"]:
                    if asset["name"] == "banner.png":
                        banner_url = asset["browser_download_url"]
                    elif asset["name"] == "changelog.txt":
                        changelog_response = requests.get(asset["browser_download_url"])
                        changelog_content = changelog_response.text

                if banner_url:
                    banner_response = requests.get(banner_url)
                    banner_path = "/tmp/onigiri_banner.png"
                    with open(banner_path, "wb") as f:
                        f.write(banner_response.content)
                    
                    GLib.idle_add(self.update_ui, banner_path, changelog_content)
            except Exception as e:
                GLib.idle_add(self.show_error, str(e))

        thread = threading.Thread(target=check)
        thread.daemon = True
        thread.start()

    def update_ui(self, banner_path, changelog):
        self.banner_image.set_filename(banner_path)
        
        latest_version = self.version_info["tag_name"]
        self.version_label.set_markup(
            f"<big><b>Current version:</b> {self.current_version}\n"
            f"<b>Latest version:</b> {latest_version}</big>"
        )
        
        self.changelog_buffer.set_text(changelog)
        
        # Abilita il pulsante di aggiornamento solo se c'è una nuova versione
        self.update_button.set_sensitive(latest_version != self.current_version)

    def show_error(self, message):
        dialog = Adw.MessageDialog(
            transient_for=self.win,
            heading="Error",
            body=f"An error occurred: {message}"
        )
        dialog.add_response("ok", "OK")
        dialog.present()

    def install_update(self, button):
        dialog = Adw.MessageDialog(
            transient_for=self.win,
            heading="Updating...",
            body="Downloading and installing update..."
        )
        dialog.present()
        
        def do_update():
            try:
                # Create temporary directory for update files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Download all update assets
                    for asset in self.version_info["assets"]:
                        if asset["name"].endswith(('.pkg.tar.zst', '.pkg.tar.xz')):  # Package files
                            print(f"Downloading {asset['name']}...")
                            response = requests.get(asset["browser_download_url"])
                            
                            asset_path = os.path.join(temp_dir, asset["name"])
                            with open(asset_path, "wb") as f:
                                f.write(response.content)
                            
                            # Install package using pacman
                            subprocess.run(["sudo", "pacman", "-U", "--noconfirm", asset_path], check=True)
                    
                    # Update version file
                    config_dir = Path("/etc/onigirilinux")
                    config_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open(config_dir / "version", "w") as f:
                        f.write(self.version_info["tag_name"])
                    
                    self.current_version = self.version_info["tag_name"]
                    GLib.idle_add(self.update_ui, None, "")
                    GLib.idle_add(dialog.close)
                    GLib.idle_add(lambda: self.show_success("Update completed successfully!"))
                    
            except Exception as e:
                GLib.idle_add(dialog.close)
                GLib.idle_add(lambda: self.show_error(str(e)))

        thread = threading.Thread(target=do_update)
        thread.daemon = True
        thread.start()

    def show_success(self, message):
        dialog = Adw.MessageDialog(
            transient_for=self.win,
            heading="Success",
            body=message
        )
        dialog.add_response("ok", "OK")
        dialog.present()

if __name__ == "__main__":
    app = OnigiriUpdater()
    app.run(None)
