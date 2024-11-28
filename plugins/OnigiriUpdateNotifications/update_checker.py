#!/usr/bin/env python3
import gi
import requests
import json
import time
from pathlib import Path
import threading

gi.require_version('Notify', '0.7')
from gi.repository import Notify, GLib

class UpdateChecker:
    def __init__(self):
        Notify.init("OnigiriUpdateNotifications")
        self.current_version = self._get_current_version()
        
    def _get_current_version(self):
        try:
            with open("/etc/onigirilinux/version", "r") as f:
                return f.read().strip()
        except:
            return "1.0.0"
    
    def check_updates(self):
        try:
            response = requests.get("https://api.github.com/repos/onigirilinux/onigirilinux/releases/latest")
            if response.status_code == 200:
                latest_version = response.json()["tag_name"]
                if latest_version != self.current_version:
                    self._show_notification(latest_version)
        except Exception as e:
            print(f"Error checking updates: {str(e)}")
    
    def _show_notification(self, new_version):
        notification = Notify.Notification.new(
            "OnigiriLinux Update Available",
            f"Version {new_version} is now available.\nOpen Update Manager to install.",
            "system-software-update"
        )
        notification.set_urgency(Notify.Urgency.NORMAL)
        notification.show()
    
    def start_monitoring(self):
        def check_loop():
            while True:
                self.check_updates()
                time.sleep(3600)  # Check every hour
        
        thread = threading.Thread(target=check_loop)
        thread.daemon = True
        thread.start()

def main():
    checker = UpdateChecker()
    checker.start_monitoring()
    GLib.MainLoop().run()

if __name__ == "__main__":
    main()
