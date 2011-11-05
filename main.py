import sys, os
import imp
from twisted.internet import reactor
from twisted.python import log
from mlog import getLogger

# Our modules.
from config import OptionsParser

# The layout of this program is as follows:
# 
#   scripts/
#     *.py
#   connectors/
#     *.py
#   
# Each script in the scripts/ directory will be loaded and an instance of 
# the ScriptHandler() class is created and added to our list.
# 
# For each connector in the connectors/ directory will be loaded, and the 
# method checkEnabled() is called.  If it returns True, an instance of the
# Connector() class is created and added to our list.
# 
# 



# Given a file path, imports it and returns the module.
def importFile(filePath):
    try:
        _, name = os.path.split(filePath)
        name, ext = os.path.splitext(name)
        
        mod = imp.load_source(name, filePath)
        return mod
    except Exception, e:
        getLogger(__name__).debug('Error importing file: ' + filePath + str(e))
        return None


class MainHandler(object):
    _connectors = []
    _handlers = []
    
    def addConnector(self, connector):
        self._connectors.append(connector)
        
    def addScriptHandler(self, handler):
        self._handlers.append(handler)
        
    def initConnectors(self):
        """Initializes our connectors by giving them a handler function."""
        
        def handlerFunc(message, responseFunc):
            for h in self._handlers:
                h.handleMessage(message, responseFunc)
        
        getLogger(__name__).debug('Initializing %d connectors...' % len(self._connectors))
        for c in self._connectors:
            c.initialize(handlerFunc)



def main():
    # Get logger.
    mlog = getLogger(__name__)
    mlog.debug('PyChatBot started.')
    
    # Open our options file.
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        mlog.debug('Defaulting to filename options.ini')
        fname = 'options.ini'
    
    try:
        mlog.debug('Opening our config file: ' + fname)
        parser = OptionsParser(fname)
    except IOError:
        mlog.critical("Could not open config file!")
        return
        
    # Create main class.
    mlog.debug('Creating main handler...')
    mh = MainHandler()
    
    # Load scripts.
    try:
        mlog.info('Looking for scripts...')
        scriptFiles = [x for x in os.listdir('scripts') if os.path.splitext(x)[1] == '.py']
    except WindowsError:
        mlog.error('Could not list scripts directory!')
        scriptFiles = []
    
    mlog.debug('Found ' + str(len(scriptFiles)) + ' script files.')
    
    mlog.debug('Loading scripts...')
    loadedCount = 0
    for f in scriptFiles:
        m = importFile(os.path.join('scripts', f))
        if m:
            mh.addScriptHandler(m.ScriptHandler(parser))
            loadedCount += 1
            mlog.debug('Loaded and imported: ' + f)
        else:
            mlog.debug('Could not import file: ' + f)
            
    # Loaded them all!
    mlog.info('Loaded ' + str(loadedCount) + ' scripts.')
    
    # Load connectors.
    try:
        mlog.info('Looking for connectors...')
        connectorFiles = [x for x in os.listdir('connectors') if os.path.splitext(x)[1] == '.py']
    except WindowsError:
        mlog.error('Could not list connectors directory!')
        connectorFiles = []
    
    mlog.debug('Found ' + str(len(connectorFiles)) + ' connector files.')
    
    loadedCount = 0
    for f in connectorFiles:
        m = importFile(os.path.join('connectors', f))
        if m:
            conn = m.Connector(parser)
            if conn.checkEnabled():
                mh.addConnector(conn)
                mlog.debug('Loaded and imported: ' + f)
                loadedCount += 1
            else:
                mlog.debug('Imported disabled: ' + f)
        else:
            mlog.debug('Could not import file: ' + f)
    
    mlog.info('Loaded ' + str(loadedCount) + ' connectors.')
    
    # Initialize our connectors.
    mlog.info('Initializing connectors...')
    mh.initConnectors()
    
    # END OF INITIALIZATION
    # ----------------------------------------------------------------------------------------------------
    # Start Twisted reactor.
    mlog.info('Initializing done.  Starting Twisted reactor.')
    reactor.run()



if __name__ == "__main__":
    main()