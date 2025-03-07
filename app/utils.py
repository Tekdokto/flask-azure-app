import logging
import os

def setup_logger():
    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    log_directory = os.path.join(base_dir, "../logs") 
    os.makedirs(log_directory, exist_ok=True)
    log_file_path = os.path.join(log_directory, "app.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]

    )

    return logging.getLogger(__name__)

logger = setup_logger()