import os
from rembg import remove
from PIL import Image

CONFIG_FILE = "app_initialized.flag"
INPUT_IMG = "asset/logo.jpg"
OUTPUT_IMG = "asset/logo_transparent.png"

def run_first_launch_setup():
    # Check if first launch has already occurred
    if not os.path.exists(CONFIG_FILE):
        print("First launch detected: Processing image background...")
        
        if os.path.exists(INPUT_IMG):
            input_image = Image.open(INPUT_IMG)
            output_image = remove(input_image)
            output_image.save(OUTPUT_IMG)
            print("Background removed successfully.")
        
        # Create flag file to prevent running on future launches
        with open(CONFIG_FILE, "w") as f:
            f.write("initialized=true")

# Call this function inside your app's startup routine
if __name__ == "__main__":
    run_first_launch_setup()
    # Start app main loop / server here...
