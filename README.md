# Real Time Image Resizer

A powerful Python-based image processing application with a modern web interface for bulk image resizing operations. Built with Eel for seamless desktop-web integration.

## Features

- Real-time folder monitoring for automatic image processing
- Multiple resize options:
  - Scale by percentage
  - Fixed width/height with aspect ratio preservation
- Batch processing capability
- Support for multiple image formats (PNG, JPEG, GIF, etc.)
- Progress tracking with detailed status updates
- Error handling and logging
- Clean and responsive web interface

## Prerequisites

- Python 3.6 or higher
- Web browser (Chrome recommended)
- Windows/Linux/MacOS compatible

## Installation

1. Clone the repository:

```bash
git clone https://github.com/kmkavinda6/RealTime_ImageResizer.git
cd RealTime_ImageResizer
```

2. Create and activate virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure

```
RealTime_ImageResizer/
│
├── main.py               # Entry point for the application
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
│
├── modules/              # Application modules
│   ├── file_watcher.py   # Handles folder monitoring
│   ├── image_processor.py # Resizes images
│   ├── gui.py            # User interface code
│   └── logger.py         # Logging configuration
│
└── web/                  # Web interface files
    ├── index.html        # Main HTML interface
    ├── css/
    │   └── style.css     # CSS styles
    └── js/
        └── app.js        # JavaScript application logic
```

## Usage

1. Start the application:

```bash
python main.py
```

2. Configure Settings:

   - Select source folder (where your original images are)
   - Choose destination folder (where processed images will be saved)
   - Select resize method and parameters
   - Set file format preferences

3. Processing Options:
   - "Start Processing": Begin monitoring and processing
   - "Stop Processing": End the monitoring session
   - "Reset": Clear current settings
   - "View Logs": Check processing history



## Troubleshooting

Common issues and solutions:

- Permission errors: Run with appropriate privileges
- Port conflicts: Change default port in app.py
- Image corruption: Verify source file integrity

## Contributing

1. Fork the repository
2. Create your feature branch
3. Submit pull request with clear description

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Eel framework developers
- Pillow library contributors
- All contributors and users

