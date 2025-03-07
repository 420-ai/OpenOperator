import cv2
import os
from PIL import Image

def extract_frames(video_path, num_frames=11):
     # Get the directory of the video file
    video_dir = os.path.dirname(video_path)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Error: Invalid FPS value.")
        return []

    frame_intervals = [int(i * fps) for i in range(num_frames)]
    
    frame_count = 0
    captured_count = 0
    images = []

    while cap.isOpened() and captured_count < num_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count in frame_intervals:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image = image.resize((256, 256))  # Resize to 256x256 as expected by Magma
            images.append(image)

            # Save frame as an image file in the same directory as the video
            frame_filename = os.path.join(video_dir, f"frame_{captured_count:03d}.png")
            image.save(frame_filename)
            print(f"Saved: {frame_filename}")

            captured_count += 1
        
        frame_count += 1

    cap.release()
    print(f"Extracted {len(images)} frames.")
    return images
