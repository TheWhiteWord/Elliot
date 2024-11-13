import os
import datetime
import shutil

class ErrorLogger:
    def __init__(self, log_file="logs/error_log.txt"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _log(self, level, context, message):
        """
        Internal logging method to handle all types of log entries.
        Args:
            level (str): Log level (e.g., ERROR, WARNING, INFO).
            context (str): Context of the log entry.
            message (str): Log message.
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - {level} in {context}: {message}\n"

        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(f"Logged {level.lower()}: {log_entry.strip()}")

    def log_error(self, context, error_message):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - ERROR in {context}: {error_message}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(f"Logged error: {log_entry.strip()}")

    def log_info(self, context, info_message):
        """
        Log general informational messages.
        Args:
            context (str): Context of the info message (e.g., Association Cortex).
            info_message (str): Detailed information message.
        """
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - INFO in {context}: {info_message}\n"

        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(f"Logged info: {log_entry.strip()}")

    def log_warning(self, context, warning_message):
        """Log warnings."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} - WARNING in {context}: {warning_message}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(f"Logged warning: {log_entry.strip()}")

    def archive_old_logs(self, retention_days=7):
        """Archive logs older than the specified retention period."""
        try:
            # Ensure archive directory exists
            archive_dir = "logs/archive/"
            os.makedirs(archive_dir, exist_ok=True)

            # Check log file modification time
            if not os.path.exists(self.log_file):
                return "No logs to archive."

            modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.log_file))
            current_time = datetime.datetime.now()
            retention_period = datetime.timedelta(days=retention_days)

            if current_time - modified_time > retention_period:
                archive_path = os.path.join(
                    archive_dir, f"error_log_{modified_time.strftime('%Y%m%d')}.txt"
                )
                shutil.move(self.log_file, archive_path)
                return f"Archived log to {archive_path}."
            else:
                return "No logs older than the retention period to archive."
        except Exception as e:
            self.log_error("Failed to archive logs", str(e))
            return f"Error during log archival: {e}"
    
    def _write_log(self, log_entry):
        with open(self.log_file, "a") as file:
            file.write(log_entry)
        print(log_entry.strip())

    
