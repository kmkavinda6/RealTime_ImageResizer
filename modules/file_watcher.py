
import os
import time
import threading
import json
import eel
from typing import List, Set

class FileWatcher:
    """Class that handles monitoring folders for new image files"""
    
    def __init__(self, image_processor, logger):
        """Initialize the file watcher with image processor and logger"""
        self.image_processor = image_processor
        self.logger = logger
        self.running = False
        self.watcher_thread = None
        self.processed_images = set()
    
    def get_image_files(self, folder: str) -> List[str]:
        """Get all image files from a folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return [f for f in os.listdir(folder) 
                if os.path.isfile(os.path.join(folder, f)) and 
                os.path.splitext(f)[1].lower() in image_extensions]
    
    def initial_processing(self) -> List[dict]:
        """Process all existing images in the source folder"""
        results = []
        image_files = self.get_image_files(self.image_processor.source_folder)
        
        self.logger.info(f"Starting initial processing of {len(image_files)} images")
        
        for filename in image_files:
            result = self.image_processor.process_image(filename)
            results.append(result)
            if result["success"]:
                self.processed_images.add(filename)
        
        self.logger.info(f"Initial processing complete. Processed {len(results)} files.")
        return results
    
    def watch_folder(self) -> None:
        """Watch the source folder for new images"""
        self.logger.info("Starting folder watcher...")
        while self.running:
            try:
                current_files = set(self.get_image_files(self.image_processor.source_folder))
                new_files = current_files - self.processed_images
                
                for filename in new_files:
                    if not self.running:
                        break
                    
                    self.logger.info(f"Processing new file: {filename}")
                    result = self.image_processor.process_image(filename)
                    if result["success"]:
                        self.processed_images.add(filename)
                        # Send update to the UI
                        eel.updateProcessingStatus(json.dumps(result))
                
                # Sleep for a short time before checking again
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in watcher thread: {str(e)}")
                time.sleep(5)  # Sleep longer on error
    
    def start(self) -> bool:
        """Start the processing and watching thread"""
        if self.running:
            return False
        
        if not self.image_processor.source_folder or not self.image_processor.destination_folder:
            self.logger.error("Cannot start watcher: Source or destination folder not set")
            return False
        
        self.running = True
        self.watcher_thread = threading.Thread(target=self.watch_folder)
        self.watcher_thread.daemon = True
        self.watcher_thread.start()
        self.logger.info("File watcher started")
        return True
    
    def stop(self) -> bool:
        """Stop the processing thread"""
        if not self.running:
            return False
        
        self.logger.info("Stopping file watcher...")
        self.running = False
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=2)
        
        self.logger.info("File watcher stopped")
        return True
    
    def get_status(self) -> dict:
        """Get the current status of the watcher"""
        return {
            "running": self.running,
            "processed_count": len(self.processed_images)
        }