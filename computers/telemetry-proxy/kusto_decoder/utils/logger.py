"""
Simple Logger utility class for logging messages to the console
"""

class Logger:
    """
    Logger utility class for outputting messages
    """
    
    @staticmethod
    def log_error(message: str) -> None:
        """
        Log an error message
        Args:
            message: Message to log
        """
        print(f"[ERROR] {message}")
    
    @staticmethod
    def log(message: str) -> None:
        """
        Log a standard message
        Args:
            message: Message to log
        """
        print(f"[INFO] {message}")
