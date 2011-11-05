import sys, os
import codecs
from ConfigParser import SafeConfigParser

class OptionsParser(object):
    def __init__(self, filename):
        self.parser = SafeConfigParser()
        self.f = codecs.open(filename, 'r', encoding='utf-8')
        
        self.parser.readfp(self.f)
    
    def getOption(self, section, value):
        if not self.parser.has_section(section):
            return None
        else:
            return self.parser.get(section, value)
    