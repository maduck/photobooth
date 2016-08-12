import ConfigParser


class Config(object):
    config_file = "settings.cfg"
    section = "photobooth"

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def get(self, key):
        return self.config.get(self.section, key)

    def getint(self, key):
        return self.config.getint(self.section, key)

    def getfloat(self, key):
        return self.config.getfloat(self.section, key)

    def getboolean(self, key):
        return self.config.getboolean(self.section, key)
