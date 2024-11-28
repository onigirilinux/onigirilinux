#!/usr/bin/env python3
import gi
import cairo
import math
from Xlib import display, X
from Xlib.ext import randr
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Gtk, Gdk, GLib, Wnck

class StageManager:
    def __init__(self):
        self.screen = Wnck.Screen.get_default()
        self.screen.force_update()
        self.is_active = False
        self.gesture_start = None
        self.setup_gesture_detection()
        
    def setup_gesture_detection(self):
        # Setup X11 display and root window for gesture detection
        self.display = display.Display()
        self.root = self.display.screen().root
        
        # Get screen dimensions
        self.screen_width = self.display.screen().width_in_pixels
        self.screen_height = self.display.screen().height_in_pixels
        
        # Setup gesture area (bottom-left corner)
        self.gesture_area = {
            'x': 0,
            'y': self.screen_height - 50,
            'width': 50,
            'height': 50
        }
        
        # Start gesture detection thread
        thread = threading.Thread(target=self._monitor_gestures)
        thread.daemon = True
        thread.start()
    
    def _monitor_gestures(self):
        self.root.change_attributes(event_mask=X.PointerMotionMask | X.ButtonPressMask | X.ButtonReleaseMask)
        
        while True:
            event = self.display.next_event()
            
            if event.type == X.ButtonPress:
                if self._is_in_gesture_area(event.root_x, event.root_y):
                    self.gesture_start = (event.root_x, event.root_y)
            
            elif event.type == X.ButtonRelease:
                if self.gesture_start:
                    end_x, end_y = event.root_x, event.root_y
                    if self._is_diagonal_gesture(self.gesture_start[0], self.gesture_start[1], end_x, end_y):
                        GLib.idle_add(self.toggle_stage_manager)
                    self.gesture_start = None
    
    def _is_in_gesture_area(self, x, y):
        return (x >= self.gesture_area['x'] and 
                x <= self.gesture_area['x'] + self.gesture_area['width'] and
                y >= self.gesture_area['y'] and 
                y <= self.gesture_area['y'] + self.gesture_area['height'])
    
    def _is_diagonal_gesture(self, start_x, start_y, end_x, end_y):
        # Check if gesture is diagonal from bottom-left to top-right
        dx = end_x - start_x
        dy = start_y - end_y  # Inverted because Y grows downward
        
        if dx > 100 and dy > 100:  # Minimum gesture distance
            angle = math.degrees(math.atan2(dy, dx))
            return 35 <= angle <= 55  # Accept angles around 45 degrees
        return False
    
    def toggle_stage_manager(self):
        if not self.is_active:
            self.show_stage_manager()
        else:
            self.hide_stage_manager()
        self.is_active = not self.is_active
    
    def show_stage_manager(self):
        self.window = Gtk.Window()
        self.window.set_title("Stage Manager")
        self.window.set_default_size(self.screen_width, self.screen_height)
        
        # Make window transparent
        self.window.set_app_paintable(True)
        screen = self.window.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.window.set_visual(visual)
        
        # Create drawing area
        drawing_area = Gtk.DrawingArea()
        drawing_area.set_draw_func(self._draw_stage_manager)
        
        self.window.set_child(drawing_area)
        self.window.present()
        
        # Add close button
        close_button = Gtk.Button(label="Close All")
        close_button.connect("clicked", self._close_all_windows)
        close_button.set_halign(Gtk.Align.END)
        close_button.set_valign(Gtk.Align.START)
        self.window.add_overlay(close_button)
    
    def _draw_stage_manager(self, area, cr, width, height):
        # Semi-transparent background
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.paint()
        
        # Get all windows
        windows = self.screen.get_windows()
        if not windows:
            return
        
        # Calculate grid layout
        cols = math.ceil(math.sqrt(len(windows)))
        rows = math.ceil(len(windows) / cols)
        
        cell_width = width / cols
        cell_height = height / rows
        padding = 20
        
        # Draw windows
        for i, window in enumerate(windows):
            if window.get_window_type() == Wnck.WindowType.NORMAL:
                row = i // cols
                col = i % cols
                
                x = col * cell_width + padding
                y = row * cell_height + padding
                w = cell_width - (padding * 2)
                h = cell_height - (padding * 2)
                
                # Draw window preview with 3D effect
                cr.save()
                cr.set_source_rgba(1, 1, 1, 0.1)
                cr.rectangle(x + 5, y + 5, w, h)
                cr.fill()
                
                cr.set_source_rgba(1, 1, 1, 0.9)
                cr.rectangle(x, y, w, h)
                cr.fill()
                
                # Draw window title
                cr.set_source_rgba(0, 0, 0, 1)
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(14)
                title = window.get_name()
                text_extents = cr.text_extents(title)
                cr.move_to(x + (w - text_extents.width) / 2, y + h - 10)
                cr.show_text(title)
                cr.restore()
    
    def _close_all_windows(self, button):
        windows = self.screen.get_windows()
        for window in windows:
            if window.get_window_type() == Wnck.WindowType.NORMAL:
                window.close(0)
        self.hide_stage_manager()
    
    def hide_stage_manager(self):
        if hasattr(self, 'window'):
            self.window.destroy()
            self.is_active = False

def main():
    stage_manager = StageManager()
    Gtk.main()

if __name__ == "__main__":
    main()
