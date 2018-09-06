import logging
from datetime import datetime


def timestamp():
    d = datetime.utcnow()
    return round(datetime.timestamp(d))

def log(text, info=True):
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    if info == True:
        logger.info(text)
    else:
        logger.warning(text)