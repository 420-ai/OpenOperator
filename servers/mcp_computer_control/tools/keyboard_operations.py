import pyautogui
import time
from typing import List, Dict, Any, Union

def keyboard_type(text: str, interval: float = 0.01) -> Dict[str, Any]:
    """Type text string with proper character encoding."""
    try:
        if not isinstance(text, str):
            return {"success": False, "error": "Text must be a string"}
        
        pyautogui.typewrite(text, interval=interval)
        
        return {
            "success": True,
            "text": text,
            "length": len(text),
            "interval": interval
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def keyboard_hotkeys(keys: Union[str, List[str]], interval: float = 0.1) -> Dict[str, Any]:
    """Execute keyboard shortcuts (Ctrl+C, Alt+Tab, etc.)."""
    try:
        if isinstance(keys, str):
            if '+' in keys:
                key_list = [k.strip().lower() for k in keys.split('+')]
            else:
                key_list = [keys.strip().lower()]
        else:
            key_list = [k.strip().lower() for k in keys]
        
        valid_keys = {
            'ctrl', 'control', 'alt', 'shift', 'win', 'windows', 'cmd', 'command',
            'tab', 'enter', 'return', 'space', 'backspace', 'delete', 'escape', 'esc',
            'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            'insert', 'capslock', 'numlock', 'scrolllock', 'pause', 'printscreen',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        }
        
        normalized_keys = []
        for key in key_list:
            if key in ['ctrl', 'control']:
                normalized_keys.append('ctrl')
            elif key in ['win', 'windows', 'cmd', 'command']:
                normalized_keys.append('win')
            elif key in ['return']:
                normalized_keys.append('enter')
            elif key in ['esc']:
                normalized_keys.append('escape')
            elif key in valid_keys:
                normalized_keys.append(key)
            else:
                return {"success": False, "error": f"Invalid key: {key}"}
        
        if len(normalized_keys) == 1:
            pyautogui.press(normalized_keys[0])
        else:
            pyautogui.hotkey(*normalized_keys)
        
        time.sleep(interval)
        
        return {
            "success": True,
            "keys": normalized_keys,
            "original_input": keys
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def keyboard_press(key: str, presses: int = 1, interval: float = 0.1) -> Dict[str, Any]:
    """Press a specific key multiple times."""
    try:
        key = key.strip().lower()
        
        if key in ['ctrl', 'control']:
            key = 'ctrl'
        elif key in ['win', 'windows', 'cmd', 'command']:
            key = 'win'
        elif key in ['return']:
            key = 'enter'
        elif key in ['esc']:
            key = 'escape'
        
        for _ in range(presses):
            pyautogui.press(key)
            if presses > 1 and interval > 0:
                time.sleep(interval)
        
        return {
            "success": True,
            "key": key,
            "presses": presses,
            "interval": interval
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def keyboard_hold(key: str, duration: float = 1.0) -> Dict[str, Any]:
    """Hold a key down for a specified duration."""
    try:
        key = key.strip().lower()
        
        if key in ['ctrl', 'control']:
            key = 'ctrl'
        elif key in ['win', 'windows', 'cmd', 'command']:
            key = 'win'
        elif key in ['return']:
            key = 'enter'
        elif key in ['esc']:
            key = 'escape'
        
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        
        return {
            "success": True,
            "key": key,
            "duration": duration
        }
    except Exception as e:
        return {"success": False, "error": str(e)}