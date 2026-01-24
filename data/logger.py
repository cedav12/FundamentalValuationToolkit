import sys
import os

class Logger:
    """
    Redirects stdout to both terminal and a file.
    """

    def __init__(self, filename: str | None = None):
        self.terminal = sys.stdout

        if filename:
            # Create directory if needed
            log_dir = os.path.dirname(filename)

            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            self.logger = open(filename, "w", encoding="utf-8")
        else:
            self.logger = None

    def log(self, message):
        message_str = str(message) + "\n"

        # Write to console
        self.terminal.write(message_str)

        # Write to file
        if self.logger:
            self.logger.write(message_str)

        # Flush immediately
        self.flush()

    def flush(self):
        self.terminal.flush()
        if self.logger:
            self.logger.flush()

    def close(self):
        if self.logger:
            self.logger.close()