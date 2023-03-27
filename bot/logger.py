import logging
import os
import datetime

def log_to_file(log_file, text, log_level):
    log_message = format_log(text, log_level)
    
    # Create a logger
    logger = logging.getLogger(log_file)

    # Set the log level
    logger.setLevel(logging.INFO)

    # Use the with statement to create and add the file handler to the logger
    log_path = os.path.join('logs', log_file)
    file_handler = logging.FileHandler(log_path)
    # Set the log level for the file handler
    file_handler.setLevel(log_level)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    try:
        # Log the message at the specified log level
        logger.log(log_level, log_message)
    finally:
        # Close the file handler
        file_handler.close()
        # Remove the file handler from the logger
        logger.removeHandler(file_handler)
   
        
def format_log(text, log_level):
    level_name = logging.getLevelName(log_level)
    time = datetime.datetime.now()
    log_time = time.strftime("%I:%M %p, %b %d, %Y")
    return f'{level_name} - {text} - {log_time}'
    
    