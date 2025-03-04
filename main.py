import eel
import os
import sys
from modules.gui import GUI
from modules.image_processor import ImageProcessor
from modules.file_watcher import FileWatcher
from modules.logger import setup_logger

def get_app_dir():
    """Get the directory where the application is running from"""
    if getattr(sys, 'frozen', False):
        # If we're running as a bundled exe, use the directory the exe is in
        return os.path.dirname(sys.executable)
    else:
        # If we're running as a script, use the directory the script is in
        return os.path.dirname(os.path.abspath(__file__))

def main():
    # Set up logger
    logger = setup_logger('ImageResizer')
    logger.info("Starting Image Resizer application")
    
    # Initialize application components
    # app_dir = get_app_dir()
    # web_dir = os.path.join(app_dir, 'web')
    
    # Initialize Eel with the web folder
    eel.init('web')
    
    # Create application components
    image_processor = ImageProcessor(logger)
    file_watcher = FileWatcher(image_processor, logger)
    gui = GUI(image_processor, file_watcher, logger)
    
    # Start Eel with a specific size for the window
    try:
        logger.info("Starting Eel web interface")
        eel.start('index.html', size=(800, 600))
    except (SystemExit, KeyboardInterrupt):
        # Handle normal exit
        logger.info("Application closed by user")
        file_watcher.stop()
    except Exception as e:
        logger.error(f"Error in Eel app: {str(e)}")
        file_watcher.stop()

if __name__ == "__main__":
    main()