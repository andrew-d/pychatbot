

class ScriptHandler(object):
    def __init__(self, optParser):
        self._optParser = optParser
        
    def handleMessage(self, message, responseFunc):
        if message[:4].lower() == 'echo':
            responseFunc(message[4:])
    