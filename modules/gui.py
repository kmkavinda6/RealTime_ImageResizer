import eel
import os
import json
import tkinter as tk
from tkinter import filedialog

class GUI:
    """Class that handles the Eel web interface and user interactions"""
    
    def __init__(self, image_processor, file_watcher, logger):
        """Initialize the GUI with dependencies"""
        self.image_processor = image_processor
        self.file_watcher = file_watcher
        self.logger = logger
        self._register_eel_functions()
    
    def _register_eel_functions(self):
        """Register Eel exposed functions"""
        eel.expose(self.set_folders)
        eel.expose(self.set_resize_options)
        eel.expose(self.initial_processing)
        eel.expose(self.start_processing)
        eel.expose(self.stop_processing)
        eel.expose(self.get_status)
        # browse_folder is already exposed via decorator
    
    @staticmethod
    @eel.expose
    def browse_folder():
        """Open folder browser dialog and return selected path"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring the dialog to front
        folder_path = filedialog.askdirectory()
        root.destroy()
        return folder_path or ""
    
    def set_folders(self, source, destination):
        """Set source and destination folders"""
        success, message = self.image_processor.set_folders(source, destination)
        return {"success": success, "message": message}
    
    def set_resize_options(self, scaling_factor=None, single_side_resolution=None):
        """Set resize options"""
        self.image_processor.set_resize_options(scaling_factor, single_side_resolution)
        return {"success": True}
    
    def initial_processing(self):
        """Perform initial processing of all images in source folder"""
        results = self.file_watcher.initial_processing()
        return {"success": True, "results": results}
    
    def start_processing(self):
        """Start the continuous processing"""
        success = self.file_watcher.start()
        return {"success": success}
    
    def stop_processing(self):
        """Stop the continuous processing"""
        success = self.file_watcher.stop()
        return {"success": success}
    
    def get_status(self):
        """Get current status"""
        watcher_status = self.file_watcher.get_status()
        return {
            "running": watcher_status["running"],
            "source_folder": self.image_processor.source_folder,
            "destination_folder": self.image_processor.destination_folder,
            "scaling_factor": self.image_processor.scaling_factor,
            "single_side_resolution": self.image_processor.single_side_resolution,
            "processed_count": watcher_status["processed_count"]
        }