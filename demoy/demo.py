from demoy.pb.cstrike15_usermessages_public_pb2 import *
from demoy.pb.netmessages_public_pb2 import *

from demoy.parser import Parser

class BaseObj(object):
    def __init__(self, data):
        self.__dict__ = data

class Demo(object):
    def __init__(self, parser):
        self.parser = parser

    def parse(self):
        self.parser.parse()

        self.header = BaseObj(self.parser.header)

    @classmethod
    def from_file(cls, fobj):
        self = cls(Parser(fobj.read()))
        return self

    @classmethod
    def from_binary(cls, data):
        pass
