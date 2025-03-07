import cv2
import os
from PIL import Image
import numpy as np

def extract_frames(video_path, num_frames=11):
    # Get the directory of the video file
    video_dir = os.path.dirname(video_path)

    # Open the video file
    cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)

    if os.path.exists(video_path):
        print(f"Video file exists: {video_path}")
        print(f"File size: {os.path.getsize(video_path)} bytes")
    else:
        print("Video file not found")
        return []

    if not cap.isOpened():
        print("My Error: Could not open video.")
        return []
    else:
        print("Video opened successfully!")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps <= 0:
        print("Error: Invalid FPS value.")
        return []
    
    frame_intervals = [int(i * fps) for i in range(num_frames)]  # Frames to capture
    
    frame_count = 0
    captured_count = 0
    images = []
    
    while cap.isOpened() and captured_count < num_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count in frame_intervals:
            # Convert frame from BGR (OpenCV) to RGB (PIL)
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            images.append(image)

            # Save frame as an image file in the same directory as the video
            frame_filename = os.path.join(video_dir, f"frame_{captured_count:03d}.png")
            image.save(frame_filename)
            print(f"Saved: {frame_filename}")

            captured_count += 1
        
        frame_count += 1
    
    cap.release()
    print("Frame extraction complete.")
    return images
