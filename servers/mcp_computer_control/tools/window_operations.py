import platform
import subprocess
import shlex
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Platform-specific imports
platform_name = platform.system()
if platform_name == 'Windows':
    try:
        import win32gui
        import win32con
    except ImportError:
        win32gui = None
        win32con = None
elif platform_name == 'Darwin':  # macOS
    try:
        import AppKit
    except ImportError:
        AppKit = None


# Application paths configuration
APP_PATHS = {
    "chrome": {
        "Windows": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "Linux": "/usr/bin/google-chrome"
    },
    "firefox": {
        "Windows": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "Darwin": "/Applications/Firefox.app/Contents/MacOS/firefox",
        "Linux": "/usr/bin/firefox"
    },
    "notepad": {
        "Windows": "C:\\Windows\\System32\\notepad.exe",
        "Darwin": "/System/Applications/TextEdit.app/Contents/MacOS/TextEdit",
        "Linux": "/usr/bin/gedit"
    },
    "calculator": {
        "Windows": "calc.exe",
        "Darwin": "/System/Applications/Calculator.app/Contents/MacOS/Calculator",
        "Linux": "/usr/bin/gnome-calculator"
    }
}


def launch_application(command: str, shell: bool = False) -> Dict[str, Any]:
    """Launch an application by command or known app name."""
    try:
        # Check if it's a known application
        if command.lower() in APP_PATHS:
            app_path = APP_PATHS[command.lower()].get(platform_name)
            if app_path and os.path.exists(app_path):
                subprocess.Popen([app_path])
                return {
                    "success": True,
                    "message": f"{command} launched successfully",
                    "app_path": app_path,
                    "platform": platform_name
                }
        
        # Otherwise treat as a command
        if shell:
            # For shell commands, pass as string
            subprocess.Popen(command, shell=True)
        else:
            # For non-shell commands, split the string
            if isinstance(command, str):
                command_list = shlex.split(command)
            else:
                command_list = command
            
            # Expand user directory
            for i, arg in enumerate(command_list):
                if arg.startswith("~/"):
                    command_list[i] = os.path.expanduser(arg)
            
            subprocess.Popen(command_list)
        
        return {
            "success": True,
            "message": f"Application launched successfully",
            "command": command,
            "shell": shell
        }
        
    except Exception as e:
        logger.error(f"Error launching application: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def maximize_window(title_contains: str) -> Dict[str, Any]:
    """Maximize a window by title search."""
    try:
        if platform_name == 'Windows':
            if not win32gui or not win32con:
                return {"success": False, "error": "pywin32 not available on Windows"}
            
            matching_windows = []
            
            def enum_handler(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title_contains.lower() in title.lower():
                        result.append((hwnd, title))
            
            win32gui.EnumWindows(enum_handler, matching_windows)
            
            if not matching_windows:
                return {
                    "success": False,
                    "error": f"No window found containing '{title_contains}'"
                }
            
            hwnd, title = matching_windows[0]
            
            # Restore if minimized
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            # Maximize the window
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            
            return {
                "success": True,
                "message": f"Window '{title}' maximized",
                "matched_title": title,
                "window_count": len(matching_windows)
            }
            
        elif platform_name == 'Darwin':  # macOS
            # Use AppleScript to maximize window
            script = f'''
            tell application "System Events"
                set windowList to every window of every process whose name contains "{title_contains}"
                if windowList is not {{}} then
                    set targetWindow to item 1 of windowList
                    tell targetWindow
                        set value of attribute "AXFullScreen" to true
                    end tell
                    return "Window maximized"
                else
                    return "Window not found"
                end if
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if "Window maximized" in result.stdout:
                return {
                    "success": True,
                    "message": f"Window containing '{title_contains}' maximized"
                }
            else:
                return {
                    "success": False,
                    "error": f"No window found containing '{title_contains}'"
                }
                
        elif platform_name == 'Linux':
            # Use wmctrl to maximize window
            try:
                # First find windows
                result = subprocess.run(
                    ['wmctrl', '-l'],
                    capture_output=True,
                    text=True
                )
                
                matching_windows = []
                for line in result.stdout.splitlines():
                    if title_contains.lower() in line.lower():
                        window_id = line.split()[0]
                        matching_windows.append((window_id, line))
                
                if not matching_windows:
                    return {
                        "success": False,
                        "error": f"No window found containing '{title_contains}'"
                    }
                
                window_id, window_info = matching_windows[0]
                
                # Maximize the window
                subprocess.run([
                    'wmctrl', '-i', '-r', window_id,
                    '-b', 'add,maximized_vert,maximized_horz'
                ])
                
                # Bring to front
                subprocess.run(['wmctrl', '-i', '-a', window_id])
                
                return {
                    "success": True,
                    "message": f"Window maximized",
                    "window_info": window_info,
                    "window_count": len(matching_windows)
                }
                
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "wmctrl not installed. Install with: sudo apt-get install wmctrl"
                }
        else:
            return {
                "success": False,
                "error": f"Unsupported platform: {platform_name}"
            }
            
    except Exception as e:
        logger.error(f"Error maximizing window: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def list_windows() -> Dict[str, Any]:
    """List all visible windows."""
    try:
        windows = []
        
        if platform_name == 'Windows':
            if not win32gui:
                return {"success": False, "error": "pywin32 not available on Windows"}
            
            def enum_handler(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        result.append({
                            "title": title,
                            "handle": hwnd
                        })
            
            win32gui.EnumWindows(enum_handler, windows)
            
        elif platform_name == 'Linux':
            try:
                result = subprocess.run(
                    ['wmctrl', '-l'],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.splitlines():
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        windows.append({
                            "id": parts[0],
                            "desktop": parts[1],
                            "title": parts[3]
                        })
                        
            except FileNotFoundError:
                return {
                    "success": False,
                    "error": "wmctrl not installed. Install with: sudo apt-get install wmctrl"
                }
                
        elif platform_name == 'Darwin':  # macOS
            # Use AppleScript to list windows
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in application processes
                    if visible of proc is true then
                        repeat with win in windows of proc
                            set end of windowList to name of proc & " - " & name of win
                        end repeat
                    end if
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                window_titles = result.stdout.strip().split(", ")
                windows = [{"title": title} for title in window_titles if title]
        
        return {
            "success": True,
            "windows": windows,
            "count": len(windows),
            "platform": platform_name
        }
        
    except Exception as e:
        logger.error(f"Error listing windows: {e}", exc_info=True)
        return {"success": False, "error": str(e)}