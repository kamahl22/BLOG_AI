import logging

def setup_logger():
    logger = logging.getLogger('BLOG_AI')
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler('discord_bot/bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(file_handler)
    return logger
