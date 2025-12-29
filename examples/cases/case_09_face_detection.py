"""
case_09_face_detection.py
Face Detection with OpenCV — console and overlay modes

Demonstrates:
- Real-time face detection using OpenCV's Haar Cascade classifier
- Two display modes: console output and transparent overlay
- FPS counter and performance monitoring
- Clean shutdown handling
"""

import cv2
import mss
import numpy as np
import time
from transparent_overlay import Overlay

def download_haarcascade():
    """Download the haarcascade file if it doesn't exist."""
    import os
    import urllib.request
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Path to save the cascade file
    cascade_path = os.path.join('data', 'haarcascade_frontalface_default.xml')
    
    # Download if file doesn't exist
    if not os.path.exists(cascade_path):
        print("Downloading haarcascade_frontalface_default.xml...")
        url = "https://raw.githubusercontent.com/opencv/opencv/4.x/data/haarcascades/haarcascade_frontalface_default.xml"
        urllib.request.urlretrieve(url, cascade_path)
        print("Download complete!")
    
    return cascade_path

# Download or get path to the cascade file
cascade_path = download_haarcascade()

# Load the face detection classifier
face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    raise RuntimeError("Error loading face cascade classifier. Please check the file at: " + cascade_path)


def run_console_mode():
    """Run face detection with console output only."""
    import os
    import sys

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor

        print("Running in console mode. Detecting faces... (Press Ctrl+C to exit)")
        print("-" * 50)

        try:
            while True:
                start_time = time.time()

                # Capture screen
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(50, 50),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                # Clear the console
                os.system('cls' if os.name == 'nt' else 'clear')

                # Display header
                print("Face Detection - Console Mode")
                print("-" * 50)
                print(f"Status: {'Active' if len(faces) > 0 else 'No faces detected'}")
                print(f"Faces detected: {len(faces)}")

                # Display faces in a list
                if len(faces) > 0:
                    print("\nDetected faces:")
                    print("-" * 30)
                    for i, (x, y, w, h) in enumerate(faces, 1):
                        print(f"Face #{i}:")
                        print(f"  Position: ({x}, {y})")
                        print(f"  Size:     {w}x{h} px")
                        print(f"  Area:     {w * h} px²")
                        print("-" * 30)

                # Control FPS
                elapsed = time.time() - start_time
                time.sleep(max(0.05, 1 / 3 - elapsed))  # Reduced update frequency for better readability

        except KeyboardInterrupt:
            print("\nStopping console mode...")


def run_overlay_mode():
    """Run face detection with transparent overlay."""
    # Create fullscreen transparent overlay
    overlay = Overlay()
    overlay.start_layer()

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor

        print("Running in overlay mode. Detecting faces... (Press Ctrl+C to exit)")

        try:
            while True:
                start_time = time.time()

                # Clear previous frame
                overlay.frame_clear()

                # Capture screen
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(50, 50),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                # Draw for each face
                for (x, y, w, h) in faces:
                    x, y, w, h = int(x), int(y), int(w), int(h)

                    # Draw rectangle around face (red, semi-transparent)
                    overlay.draw_rect(
                        x, y, w, h,
                        color=(255, 0, 0, 200),
                        thickness=3
                    )

                    # Face info text (centered below the face)
                    info_text = f"Face: {w}x{h}"
                    text_x = x + w // 2
                    text_y = y + h + 5

                    overlay.draw_text(
                        text_x, text_y,
                        info_text,
                        color=(255, 255, 255, 255),
                        font_size=20,
                        highlight=True,
                        bg_color=(0, 0, 0, 180),
                        anchor="mt"
                    )

                    # Coordinates text
                    coords_text = f"({x},{y})"
                    coords_y = text_y + 15

                    overlay.draw_text(
                        text_x, coords_y,
                        coords_text,
                        color=(100, 50, 150, 255),
                        font_size=16,
                        highlight=False,
                        bg_color=(0, 0, 0, 120),
                        anchor="mt"
                    )

                # Show message if no faces detected
                if len(faces) == 0:
                    overlay.draw_text(
                        50, 50,
                        "No faces detected",
                        color=(200, 200, 200, 255),
                        font_size=30,
                        highlight=True
                    )

                # Update overlay
                overlay.signal_render()

                # Control FPS
                elapsed = time.time() - start_time
                time.sleep(max(0.05, 1 / 15 - elapsed))  # Target ~15 FPS

        except KeyboardInterrupt:
            print("\nStopping overlay...")
        finally:
            overlay.stop_layer()


def main():
    """Main function to run the face detection application."""
    print("Face Detection Application")
    print("1. Console mode (text output only)")
    print("2. Overlay mode (transparent overlay)")

    while True:
        choice = input("\nSelect mode (1 or 2): ").strip()
        if choice == '1':
            run_console_mode()
            break
        elif choice == '2':
            run_overlay_mode()
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
