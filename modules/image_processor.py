
import os
from pathlib import Path
from PIL import Image
from typing import Dict, Union, Tuple

class ImageProcessor:
    """Class that handles image resizing operations"""
    
    def __init__(self, logger):
        """Initialize the image processor with logger"""
        self.logger = logger
        self.source_folder = ""
        self.destination_folder = ""
        self.scaling_factor = 1.0
        self.single_side_resolution = None
    
    def set_folders(self, source: str, destination: str) -> Tuple[bool, str]:
        """Set source and destination folders"""
        if not os.path.exists(source):
            return False, f"Source folder does not exist: {source}"
        
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                self.logger.info(f"Created destination folder: {destination}")
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
    
    def get_output_filename(self, filename: str) -> str:
        """Generate output filename for a processed image"""
        name, ext = os.path.splitext(filename)
        if self.single_side_resolution:
            suffix = f"_{self.single_side_resolution}px"
        else:
            suffix = f"_x{self.scaling_factor}"
        return f"{name}{suffix}{ext}"
    
    def resize_image(self, input_path: str, output_path: str) -> bool:
        """Resize an image according to the set options, preserving orientation"""
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
                self.logger.error(f"Invalid dimensions for resizing: {new_width}x{new_height}")
                return False
            
            # Preserve EXIF data, including orientation
            try:
                exif = img.info.get('exif', None)
            except Exception:
                exif = None
                
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save with original EXIF data if available
            if exif:
                resized_img.save(output_path, exif=exif)
            else:
                resized_img.save(output_path)
                
            self.logger.info(f"Resized image saved to: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error resizing image {input_path}: {str(e)}")
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