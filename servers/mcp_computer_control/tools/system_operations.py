import platform
import psutil
import subprocess
import sys
import os
from typing import Dict, Any, Optional

def get_system_info() -> Dict[str, Any]:
    """Retrieve OS, screen resolution, and system capabilities."""
    try:
        import pyautogui
        screen_width, screen_height = pyautogui.size()
        
        return {
            "success": True,
            "os": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "screen": {
                "width": screen_width,
                "height": screen_height,
                "resolution": f"{screen_width}x{screen_height}"
            },
            "python": {
                "version": sys.version,
                "executable": sys.executable
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "cpu": {
                "count": psutil.cpu_count(),
                "percent": psutil.cpu_percent(interval=1)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_active_window() -> Dict[str, Any]:
    """Get information about currently focused application/window."""
    try:
        system = platform.system()
        
        if system == "Windows":
            return _get_active_window_windows()
        elif system == "Darwin":  # macOS
            return _get_active_window_macos()
        elif system == "Linux":
            return _get_active_window_linux()
        else:
            return {"success": False, "error": f"Unsupported OS: {system}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _get_active_window_windows() -> Dict[str, Any]:
    """Get active window on Windows."""
    try:
        import win32gui
        import win32process
        
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        
        return {
            "success": True,
            "title": window_title,
            "process_name": process.name(),
            "pid": pid,
            "position": {
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
                "width": rect[2] - rect[0],
                "height": rect[3] - rect[1]
            }
        }
    except ImportError:
        return {"success": False, "error": "pywin32 not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _get_active_window_macos() -> Dict[str, Any]:
    """Get active window on macOS."""
    try:
        from AppKit import NSWorkspace
        
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        
        return {
            "success": True,
            "title": active_app.get('NSApplicationName', 'Unknown'),
            "process_name": active_app.get('NSApplicationName', 'Unknown'),
            "pid": active_app.get('NSApplicationProcessIdentifier', 0)
        }
    except ImportError:
        return {"success": False, "error": "PyObjC not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _get_active_window_linux() -> Dict[str, Any]:
    """Get active window on Linux."""
    try:
        result = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True)
        if result.returncode != 0:
            return {"success": False, "error": "xdotool command failed"}
        
        window_id = result.stdout.strip()
        
        title_result = subprocess.run(['xdotool', 'getwindowname', window_id], capture_output=True, text=True)
        title = title_result.stdout.strip() if title_result.returncode == 0 else "Unknown"
        
        pid_result = subprocess.run(['xdotool', 'getwindowpid', window_id], capture_output=True, text=True)
        pid = int(pid_result.stdout.strip()) if pid_result.returncode == 0 else 0
        
        process_name = "Unknown"
        if pid > 0:
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                pass
        
        return {
            "success": True,
            "title": title,
            "process_name": process_name,
            "pid": pid,
            "window_id": window_id
        }
    except FileNotFoundError:
        return {"success": False, "error": "xdotool not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_python_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute Python scripts on the local machine with output capture."""
    try:
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": "completed"
            }
        finally:
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Code execution timed out after {timeout} seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def show_notification(title: str, message: str, duration: int = 5) -> Dict[str, Any]:
    """Display system notifications or alerts."""
    try:
        system = platform.system()
        
        if system == "Windows":
            try:
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(title, message, duration=duration)
                return {"success": True, "title": title, "message": message, "duration": duration}
            except ImportError:
                return {"success": False, "error": "win10toast not installed"}
        
        elif system == "Darwin":  # macOS
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script])
            return {"success": True, "title": title, "message": message}
        
        elif system == "Linux":
            subprocess.run(["notify-send", title, message])
            return {"success": True, "title": title, "message": message}
        
        else:
            return {"success": False, "error": f"Notifications not supported on {system}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}