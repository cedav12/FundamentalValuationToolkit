import sys
import os
import datetime

class Logger:
    """
    Redirects stdout to both terminal and a file.
    """

    def __init__(self, filename: str | None = None):
        self.terminal = sys.stdout
        self.log_dir = None

        if filename:
            # Create directory if needed
            self.log_dir = os.path.dirname(filename)

            if self.log_dir and not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir, exist_ok=True)
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

    def subsection(self, title: str):
        line = "=" * len(title)
        self.log(f"\n{title}\n{line}\n")

    def section(self, title: str):
        line = "=" * len(title)
        self.log(f"\n{line}\n{title}\n{line}\n")


    def flush(self):
        self.terminal.flush()
        if self.logger:
            self.logger.flush()

    def close(self):
        if self.logger:
            self.logger.close()