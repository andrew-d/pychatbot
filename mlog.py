import logging
import sys

DEFAULT_LEVEL = logging.DEBUG

def getLogger(name, level=None):
    level = level or DEFAULT_LEVEL
    
    mlog = logging.getLogger(name)
    mlog.setLevel(level)
    
    # Create handler.
    ch = logging.StreamHandler()
    
    # Create formatter.
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter and handler.
    ch.setFormatter(formatter)
    mlog.addHandler(ch)
    
    # Return it.
    return mlog