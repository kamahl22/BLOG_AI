# discord_bot/utils/logger.py
import logging

def setup_logger():
    logger = logging.getLogger('BLOG')
    logger.setLevel(logging.INFO)
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(console_handler)
    # File handler
    file_handler = logging.FileHandler('discord_bot/bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(file_handler)
    return logger