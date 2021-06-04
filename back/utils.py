import logging
import sys


class Error(Exception):
    '''
    Base clase for custom exceptions.
    '''
    message = ""
    
    def __init__ (self, message=""):
        self.message = message
        
    def __str__(self):        
        return (self.message)
    
class AlreadyExisting(Error):
    '''
    Exception raised when trying to insert into a table a value that already exists.
    '''
    pass
    
class UnknownError(Error):
    '''
    Other errors, not categorized
    '''
    pass

    

# Logging config
def logging_setup(args = None):
    
    logger = logging.getLogger()
    logger.handlers = [] # Removing default handler to avoid duplication of log messages
    logger.setLevel(logging.ERROR)
    
    h = logging.StreamHandler(sys.stderr)
    if args != None:
       h = logging.StreamHandler(args.logfile)
      
    h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    #logger.setLevel(logging.INFO)
    
    if args != None:
        if not args.quiet:
            logger.setLevel(logging.INFO)
        if args.debug:
            logger.setLevel(logging.DEBUG)

