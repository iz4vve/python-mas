import importlib
import logging


def get_logger(logger_name, logger_level=logging.INFO, file_handler=None):
    """
    Returns a logger instance with a determined formatter
    :param logger_name: name of the logger to be instantiated
    :type logger_name: str
    :param logger_level: level of logging
    :type logger_level: int (or logging.level)
    :param file_handler: name of a file to use as log file
    :type file_handler: str (valid file name)
    :return logger: logger instance
    :rtype: logging.logger
    """
    logging.shutdown()
    importlib.reload(logging)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)
    formatter = logging.Formatter(
        '[%(asctime)s]: %(name)s - %(funcName)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # generates file_handler, if required
    if file_handler:
        file_handler = logging.FileHandler(file_handler)
        file_handler.setLevel(logger_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger