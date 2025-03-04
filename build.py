import os
import sys
import shutil
import subprocess
import argparse

def check_requirements():
    """Check if required packages are installed"""
    print("Checking requirements...")
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check for other required packages
    with open("requirements.txt", "r") as f:
        requirements = f.read().splitlines()
    
    for requirement in requirements: 
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"Installed {requirement}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {requirement}")
            return False
    
    return True

def create_build_folder():
    """Create a build folder if it doesn't exist"""
    print("Creating build folder...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    os.makedirs("build")
    
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    os.makedirs("dist")

def build_application(one_file=True, debug=False):
    """Build the application using PyInstaller"""
    print("Building application...")
    
    pyinstaller_args = [
        "pyinstaller",
        "--name=ImageResizer",
        "--icon=web/img/icon.ico" if os.path.exists("web/img/icon.ico") else "",
        "--add-data=web;web",  # For Linux/Mac use web:web, for Windows use web;web
        "--collect-all=eel",   # Ensure all Eel dependencies are included
        "--collect-data=web",  # Collect all data from web folder
    ]
    
    if one_file:
        pyinstaller_args.append("--onefile")
    else:
        pyinstaller_args.append("--onedir")
    
    if not debug:
        pyinstaller_args.append("--windowed")  # No console window in production
    
    pyinstaller_args.append("main.py")
    
    # Remove empty strings
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    try:
        subprocess.check_call(pyinstaller_args)
        print("PyInstaller build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller build failed: {e}")
        return False

def copy_additional_files():
    """Copy any additional files needed for the executable"""
    print("Copying additional files...")
    
    # Create a basic README in the dist folder
    with open(os.path.join("dist", "README.txt"), "w") as f:
        f.write("Image Resizer Application\n")
        f.write("------------------------\n\n")
        f.write("This application monitors a source folder for images, resizes them, ")
        f.write("and saves them to a destination folder.\n\n")
        f.write("Instructions:\n")
        f.write("1. Launch ImageResizer.exe\n")
        f.write("2. Select source and destination folders\n")
        f.write("3. Set the desired image dimensions\n")
        f.write("4. Start monitoring\n")

def main():
    parser = argparse.ArgumentParser(description="Build script for Image Resizer application")
    parser.add_argument("--onedir", action="store_true", help="Build as a directory instead of a single file")
    parser.add_argument("--debug", action="store_true", help="Build with console window for debugging")
    args = parser.parse_args()
    
    print("=== Building Image Resizer Application ===")
    
    if not check_requirements():
        print("Failed to install requirements. Aborting build.")
        return
    
    create_build_folder()
    
    if build_application(one_file=not args.onedir, debug=args.debug):
        copy_additional_files()
        print("\nBuild completed successfully!")
        print(f"Executable can be found in the dist folder: {os.path.abspath('dist')}")
    else:
        print("\nBuild failed.")

if __name__ == "__main__":
    main()