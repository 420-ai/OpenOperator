import os
import platform
import subprocess
import shutil
import shlex
import logging
from typing import Dict, Optional
import pyautogui

logger = logging.getLogger(__name__)

# Global dictionaries to track recording processes and paths
recording_processes: Dict[str, subprocess.Popen] = {}
recording_paths: Dict[str, str] = {}

# Create recordings directory
recording_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recordings")
os.makedirs(recording_dir, exist_ok=True)

platform_name = platform.system()

# Linux-specific imports
if platform_name == 'Linux':
    try:
        from Xlib import display
    except ImportError:
        display = None


def start_recording(filename: str) -> dict:
    """Start screen recording with the given filename."""
    try:
        if not filename:
            return {"success": False, "error": "Filename is required"}
        
        if filename in recording_processes:
            return {"success": False, "error": f"Recording with name {filename} already in progress"}
        
        output_path = os.path.join(recording_dir, f"{filename}.mp4")
        recording_paths[filename] = output_path
        
        if platform_name == 'Linux':
            if display is None:
                return {"success": False, "error": "python-xlib not installed for Linux screen recording"}
            
            d = display.Display()
            screen_width = d.screen().width_in_pixels
            screen_height = d.screen().height_in_pixels
            start_command = f"ffmpeg -y -f x11grab -draw_mouse 1 -s {screen_width}x{screen_height} -i :0.0 -pix_fmt yuv420p -c:v libx264 -r 30 '{output_path}'"
            proc = subprocess.Popen(shlex.split(start_command), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        elif platform_name == 'Windows':
            screen_width, screen_height = pyautogui.size()
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                return {"success": False, "error": "ffmpeg not found in PATH"}
            
            start_command = [
                ffmpeg_path, '-y', '-f', 'gdigrab', '-draw_mouse', '1',
                '-video_size', f'{screen_width}x{screen_height}',
                '-i', 'desktop', '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264', '-r', '30', output_path
            ]
            proc = subprocess.Popen(
                start_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if platform_name == 'Windows' else 0
            )
        elif platform_name == 'Darwin':  # macOS
            # Use macOS screen recording
            screen_width, screen_height = pyautogui.size()
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                return {"success": False, "error": "ffmpeg not found in PATH"}
            
            # macOS screen recording with ffmpeg
            start_command = [
                ffmpeg_path, '-y', '-f', 'avfoundation',
                '-capture_cursor', '1', '-capture_mouse_clicks', '1',
                '-i', '1', '-r', '30', '-pix_fmt', 'yuv420p',
                '-c:v', 'libx264', output_path
            ]
            proc = subprocess.Popen(
                start_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            return {"success": False, "error": f"Unsupported platform: {platform_name}"}
        
        recording_processes[filename] = proc
        return {
            "success": True,
            "message": f"Recording started for {filename}",
            "output_path": output_path
        }
        
    except Exception as e:
        logger.error(f"Error starting recording: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def end_recording(filename: str) -> dict:
    """End the recording with the given filename."""
    try:
        if not filename or filename not in recording_processes:
            return {"success": False, "error": "No such recording in progress"}
        
        proc = recording_processes[filename]
        
        if platform_name == 'Windows':
            # Send 'q' to ffmpeg to gracefully stop
            proc.communicate(b'q')
        else:
            # On Linux/macOS, terminate the process
            proc.terminate()
        
        proc.wait()
        del recording_processes[filename]
        
        path = recording_paths.get(filename)
        if path and os.path.exists(path):
            file_size = os.path.getsize(path)
            return {
                "success": True,
                "message": f"Recording saved: {path}",
                "file_path": path,
                "file_size_bytes": file_size
            }
        else:
            return {"success": False, "error": "Recording file not found after termination"}
            
    except Exception as e:
        logger.error(f"Error ending recording: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def get_recording(filename: str) -> dict:
    """Get the recording file data for the given filename."""
    try:
        if not filename:
            return {"success": False, "error": "Filename is required"}
        
        path = os.path.join(recording_dir, f"{filename}.mp4")
        if os.path.exists(path):
            # Read the file and return as base64
            import base64
            with open(path, 'rb') as f:
                video_data = f.read()
            
            video_base64 = base64.b64encode(video_data).decode('utf-8')
            return {
                "success": True,
                "filename": f"{filename}.mp4",
                "file_path": path,
                "file_size_bytes": len(video_data),
                "video_data": video_base64
            }
        else:
            return {"success": False, "error": "Recording file not found"}
            
    except Exception as e:
        logger.error(f"Error getting recording: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def list_recordings() -> dict:
    """List all available recordings."""
    try:
        recordings = []
        if os.path.exists(recording_dir):
            for file in os.listdir(recording_dir):
                if file.endswith('.mp4'):
                    path = os.path.join(recording_dir, file)
                    recordings.append({
                        "filename": file,
                        "path": path,
                        "size_bytes": os.path.getsize(path),
                        "modified": os.path.getmtime(path)
                    })
        
        return {
            "success": True,
            "recordings": recordings,
            "total": len(recordings)
        }
    except Exception as e:
        logger.error(f"Error listing recordings: {e}", exc_info=True)
        return {"success": False, "error": str(e)}