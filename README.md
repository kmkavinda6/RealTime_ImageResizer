# Image Resizer

A Python application that monitors a source folder for images, resizes them according to specified parameters, and saves them to a destination folder. The application features a web-based user interface built with Eel.

## Features

- Monitor a source folder for new images
- Automatically resize new images as they are added
- Preserve aspect ratio using scaling factor or single-side resolution
- Web-based user interface
- Progress tracking and logging
- Avoid re-processing already processed images

## Installation

1. Clone this repository or download the source code.
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python app.py
```

2. In the web interface:
   - Select source and destination folders
   - Choose a resize method (scaling factor or single-side resolution)
   - Click "Start Processing" to begin
   - Click "Stop Processing" to end the monitoring

## Resize Methods

- **Scaling Factor**: Resize the image by multiplying both width and height by the specified factor (e.g., 0.5 for half size)
- **Single Side Resolution**: Resize the image so that the longest side matches the specified resolution in pixels, preserving the aspect ratio

## Project Structure

- `app.py`: Main application file with Eel setup and image processing logic
- `web/`: Contains the web interface files
  - `index.html`: Main HTML interface
  - `css/style.css`: CSS styles
  - `js/app.js`: JavaScript for the user interface

## Dependencies

- Python 3.6+
- Eel (for the web interface)
- Pillow (for image processing)

## License

MIT