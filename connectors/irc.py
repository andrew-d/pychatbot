from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from mlog import getLogger


CONFIG_SECTION = 'irc_connector'


class IrcChatBot(irc.IRCClient):
    """This class is instantiated upon connection and handles incoming messages."""
    
    def signedOn(self):
        self.log = self.factory.log
        self.channel = self.factory.channel
        self.nickname = self.factory.nickname
        
        self.join(self.channel)
        self.log.info("Signed on as %s.", self.nickname)
    
    def joined(self, channel):
        self.log.info("Joined %s.", channel)
    
    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        
        self.log.debug("Received message from user %s to %s: %s", user, channel, msg)
        
        # Only handle messages addressed to the channel as a whole.
        if channel == self.channel:
            # Check if this is addressed to us.
            if msg.startswith( self.nickname + ":" ):
                # Get the message.
                message = msg[len(self.nickname) + 1:].lstrip()
                
                # Handle it.
                self.log.debug('Handling message: ' + message)
                self.handleMessage(message, lambda msg: self.trysay(user + ': ' + msg))
                
    def trysay( self, msg ):
        """
        Attempts to send the given message to the channel.
        """
        if self.channel:
            try:
                self.say( self.channel, msg )
                return True
            except Exception, e:
                self.log.error("Error saying: ", str(e))
    
    def handleMessage(self, message, responseFunc):
        return self.factory.handleMessage(message, responseFunc)
                

class IrcChatBotFactory(protocol.ClientFactory):
    """ This class creates our individual chat bot instances, and handles re-connections. """
    
    protocol = IrcChatBot
    
    def __init__(self, channel, nickname='PyChatBot'):
        self.channel = channel
        self.nickname = nickname
        self.log = getLogger(__name__)
    
    def clientConnectionLost(self, connector, reason):
        self.log.warn("Lost connection (%s), reconnecting...", reason)
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        self.log.error("Could not connect: %s", reason)
        
    def handleMessage(self, message, responseFunc):
        self.handler(message, responseFunc)
    
    def _get_handler(self):
        return self._handler
    
    def _set_handler(self, f):
        self._handler = f
    
    handler = property(_get_handler, _set_handler)



class Connector(object):
    """ This is our connector - when initialize() is called, starts trying to connect. """
    
    def __init__(self, optParser):
        self._optParser = optParser
        self._log = getLogger(__name__)
        
        self._channel  = optParser.getOption(CONFIG_SECTION, 'channel')
        self._nick     = optParser.getOption(CONFIG_SECTION, 'nick') or 'PyChatBot'
        self._hostname = optParser.getOption(CONFIG_SECTION, 'hostname')
        self._port     = optParser.getOption(CONFIG_SECTION, 'port') or '6667'
        
        # Convert the port to a numeric value
        self._port     = int(self._port)
        
        # Convert the various text values from Unicode.
        if isinstance(self._channel, unicode):  self._channel = self._channel.encode('utf-8')
        if isinstance(self._hostname, unicode): self._hostname = self._hostname.encode('utf-8')
        if isinstance(self._nick, unicode):     self._nick = self._nick.encode('utf-8')
        
        self._log.info('Connecting to ' + str(self._hostname) + ':' + str(self._port) + 
                       ', channel ' + str(self._channel) + ', with nick ' + str(self._nick))
        
        self._factory = IrcChatBotFactory(self._channel, self._nick)

    def checkEnabled(self):
        """ Check if we're enabled by reading our options parser. """
        opt = self._optParser.getOption(CONFIG_SECTION, 'enabled')
        
        if not opt:
            return False
        
        if opt.lower() == 'true' or opt.lower() == 'yes' or opt == '1':
            return True
        else:
            return False
        
    __initcount = 0
    
    def initialize(self, handlerFunc):
        self.__initcount += 1
        
        self._log.debug('Trying to connect... %d' % self.__initcount)
        self._factory.handler = handlerFunc
        reactor.connectTCP(self._hostname, self._port, self._factory)




