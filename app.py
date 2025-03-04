import eel
import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Union, Tuple
import logging
from PIL import Image
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ImageResizer')

# Initialize eel with the web folder
def init_eel():
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # If we're running as a bundled exe, use the directory the exe is in
        app_dir = os.path.dirname(sys.executable)
    else:
        # If we're running as a script, use the directory the script is in
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    web_dir = os.path.join(app_dir, 'web')
    eel.init(web_dir)

# Image processor class
class ImageProcessor:
    def __init__(self):
        self.source_folder = ""
        self.destination_folder = ""
        self.scaling_factor = 1.0
        self.single_side_resolution = None
        self.running = False
        self.watcher_thread = None
        self.processed_images = set()
    
    def set_folders(self, source: str, destination: str) -> Tuple[bool, str]:
        """Set source and destination folders"""
        if not os.path.exists(source):
            return False, f"Source folder does not exist: {source}"
        
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                logger.info(f"Created destination folder: {destination}")
            except Exception as e:
                return False, f"Failed to create destination folder: {str(e)}"
        
        self.source_folder = source
        self.destination_folder = destination
        return True, "Folders set successfully"
    
    def set_resize_options(self, scaling_factor: float = None, single_side_resolution: int = None) -> None:
        """Set resizing options"""
        if scaling_factor is not None:
            self.scaling_factor = float(scaling_factor)
        if single_side_resolution is not None:
            self.single_side_resolution = int(single_side_resolution)
    
    def get_image_files(self, folder: str) -> List[str]:
        """Get all image files from a folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return [f for f in os.listdir(folder) 
                if os.path.isfile(os.path.join(folder, f)) and 
                os.path.splitext(f)[1].lower() in image_extensions]
    
    def get_output_filename(self, filename: str) -> str:
        """Generate output filename for a processed image"""
        name, ext = os.path.splitext(filename)
        if self.single_side_resolution:
            suffix = f"_{self.single_side_resolution}px"
        else:
            suffix = f"_x{self.scaling_factor}"
        return f"{name}{suffix}{ext}"
    
    def resize_image(self, input_path: str, output_path: str) -> bool:
        """Resize an image according to the set options"""
        try:
            img = Image.open(input_path)
            original_width, original_height = img.size
            
            if self.single_side_resolution:
                # Resize based on single side resolution
                if original_width > original_height:
                    # Landscape orientation
                    new_width = self.single_side_resolution
                    new_height = int(original_height * (new_width / original_width))
                else:
                    # Portrait orientation
                    new_height = self.single_side_resolution
                    new_width = int(original_width * (new_height / original_height))
            else:
                # Resize based on scaling factor
                new_width = int(original_width * self.scaling_factor)
                new_height = int(original_height * self.scaling_factor)
            
            # Check if the dimensions are valid
            if new_width <= 0 or new_height <= 0:
                logger.error(f"Invalid dimensions for resizing: {new_width}x{new_height}")
                return False
                
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_img.save(output_path)
            logger.info(f"Resized image saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error resizing image {input_path}: {str(e)}")
            return False
    
    def process_image(self, filename: str) -> Dict[str, Union[bool, str]]:
        """Process a single image"""
        input_path = os.path.join(self.source_folder, filename)
        output_filename = self.get_output_filename(filename)
        output_path = os.path.join(self.destination_folder, output_filename)
        
        result = {
            "filename": filename,
            "success": False,
            "output_path": output_path,
            "status": ""
        }
        
        # Check if the file already exists in destination
        if os.path.exists(output_path):
            # Check if source file is newer than destination
            src_mtime = os.path.getmtime(input_path)
            dst_mtime = os.path.getmtime(output_path)
            
            if src_mtime <= dst_mtime:
                result["status"] = "Already processed"
                result["success"] = True
                return result
        
        # Process the image
        if self.resize_image(input_path, output_path):
            result["success"] = True
            result["status"] = "Processed successfully"
        else:
            result["status"] = "Processing failed"
        
        return result
    
    def initial_processing(self) -> List[Dict[str, Union[bool, str]]]:
        """Process all existing images in the source folder"""
        results = []
        image_files = self.get_image_files(self.source_folder)
        
        for filename in image_files:
            result = self.process_image(filename)
            results.append(result)
            if result["success"]:
                self.processed_images.add(filename)
        
        return results
    
    def watch_folder(self) -> None:
        """Watch the source folder for new images"""
        logger.info("Starting folder watcher...")
        while self.running:
            try:
                current_files = set(self.get_image_files(self.source_folder))
                new_files = current_files - self.processed_images
                
                for filename in new_files:
                    if not self.running:
                        break
                    
                    result = self.process_image(filename)
                    if result["success"]:
                        self.processed_images.add(filename)
                        # Send update to the UI
                        eel.updateProcessingStatus(json.dumps(result))
                
                # Sleep for a short time before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in watcher thread: {str(e)}")
                time.sleep(5)  # Sleep longer on error
    
    def start_processing(self) -> bool:
        """Start the processing and watching thread"""
        if self.running:
            return False
        
        if not self.source_folder or not self.destination_folder:
            return False
        
        self.running = True
        self.watcher_thread = threading.Thread(target=self.watch_folder)
        self.watcher_thread.daemon = True
        self.watcher_thread.start()
        return True
    
    def stop_processing(self) -> bool:
        """Stop the processing thread"""
        if not self.running:
            return False
        
        self.running = False
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.watcher_thread.join(timeout=2)
        
        return True
    
    def get_status(self) -> Dict:
        """Get the current status of the processor"""
        return {
            "running": self.running,
            "source_folder": self.source_folder,
            "destination_folder": self.destination_folder,
            "scaling_factor": self.scaling_factor,
            "single_side_resolution": self.single_side_resolution,
            "processed_count": len(self.processed_images)
        }

# Create the image processor instance
processor = ImageProcessor()

# Eel exposed functions
@eel.expose
def set_folders(source, destination):
    success, message = processor.set_folders(source, destination)
    return {"success": success, "message": message}

@eel.expose
def set_resize_options(scaling_factor=None, single_side_resolution=None):
    processor.set_resize_options(scaling_factor, single_side_resolution)
    return {"success": True}

@eel.expose
def initial_processing():
    results = processor.initial_processing()
    return {"success": True, "results": results}

@eel.expose
def start_processing():
    success = processor.start_processing()
    return {"success": success}

@eel.expose
def stop_processing():
    success = processor.stop_processing()
    return {"success": success}

@eel.expose
def get_status():
    return processor.get_status()

# Main function
def main():
    init_eel()
    # Start Eel with a specific size for the window
    try:
        eel.start('index.html', size=(800, 600))
    except (SystemExit, KeyboardInterrupt):
        # Handle normal exit
        processor.stop_processing()
    except Exception as e:
        logger.error(f"Error in Eel app: {str(e)}")
        processor.stop_processing()

if __name__ == "__main__":
    main()