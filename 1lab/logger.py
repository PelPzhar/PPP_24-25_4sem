import logging

class Logger:
    def __init__(self, filename):
        logging.basicConfig(
            filename=filename,
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            encoding="utf-8"  # Явно задаём UTF-8
        )

    def log(self, message):
        logging.info(message)