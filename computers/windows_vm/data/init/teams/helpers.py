import win32gui
import time

def log_all_visible_windows(self):
        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                results.append((hwnd, window_title, class_name))

        windows = []
        win32gui.EnumWindows(enum_handler, windows)

        self.log("Logging all visible windows:")
        for hwnd, title, class_name in windows:
            self.log(f"HWND: {hwnd}, Title: '{title}', Class: '{class_name}'")

        return windows

def wait_for_window(self, window_title_substring=None, window_class=None, timeout=60):
    """
    Wait until a window with the given title substring or class name appears.
    
    :param window_title_substring: A part of the window title to search for.
    :param window_class: The exact class name of the window (if known).
    :param timeout: Maximum time in seconds to wait before giving up.
    """
    self.log(f"Waiting for window (title contains: '{window_title_substring}', class: '{window_class}') to appear...")

    start_time = time.time()

    while time.time() - start_time < timeout:
        log_all_visible_windows(self)

        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                cls = win32gui.GetClassName(hwnd)

                if (window_title_substring and window_title_substring.lower() in title.lower()) or \
                   (window_class and cls == window_class):
                    results.append(hwnd)

        found_windows = []
        win32gui.EnumWindows(enum_handler, found_windows)

        if found_windows:
            self.log(f"Window detected! HWND: {found_windows[0]}")
            return found_windows[0]  # Return the first found window handle

        self.log("Window not found yet, retrying...")
        time.sleep(1)

    self.log("Timeout reached! Window did not appear.")
    return None  # Return None if the window never appears

def wait_for_window_to_disappear(self, window_title_substring=None, window_class=None, timeout=60):
    """
    Wait until a window with the given title substring or class name disappears.
    
    :param window_title_substring: A part of the window title to search for.
    :param window_class: The exact class name of the window (if known).
    :param timeout: Maximum time in seconds to wait before giving up.
    """
    self.log(f"Waiting for window (title contains: '{window_title_substring}', class: '{window_class}') to disappear...")

    start_time = time.time()

    while time.time() - start_time < timeout:
        log_all_visible_windows(self)
        
        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                cls = win32gui.GetClassName(hwnd)

                if (window_title_substring and window_title_substring.lower() in title.lower()) or \
                   (window_class and cls == window_class):
                    results.append(hwnd)

        found_windows = []
        win32gui.EnumWindows(enum_handler, found_windows)

        if not found_windows:
            self.log("Window has disappeared.")
            return True  # Window is gone

        self.log("Window still present, retrying...")
        time.sleep(1)

    self.log("Timeout reached! Window did not disappear.")
    return False  # Window never disappeared