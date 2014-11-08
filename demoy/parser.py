from demoy.pb.cstrike15_usermessages_public_pb2 import *
from demoy.pb.netmessages_public_pb2 import *

import struct, logging

log = logging.getLogger(__name__)

class Buffer(object):
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def set(self, i):
        self.pos = 0

    def read(self, c):
        self.pos += c
        buf = self.data[(self.pos - c):(self.pos + c)]
        return buf

    def size(self):
        return len(self.data)

    def next(self):
        self.data += 1
        return self.data[pos]

class Command(object):
    CMD_SIGNON = 1
    CMD_PACKET = 2
    CMD_SYNCTICK = 3
    CMD_CONSOLECMD = 4
    CMD_USERCMD = 5
    CMD_DATATABLES = 6
    CMD_STOP = 7
    CMD_CUSTOMDATA = 8
    CMD_STRINGTABLES = 9

class Parser(object):
    DEMO_HEADER_STRUCT_FMT = "@8sii260s260s260s260sfiii"
    DEMO_HEADER_FIELDS = [
        "format",
        "demo_proto",
        "net_proto",
        "server_name",
        "client_name",
        "map_name",
        "game_path",
        "time",
        "ticks",
        "frames",
        "signonlength"
    ]

    DATA_COMMANDS = (
        Command.CMD_CONSOLECMD,
        Command.CMD_DATATABLES,
        Command.CMD_STRINGTABLES
    )

    def __init__(self, data):
        self.data = Buffer(data)
        self.header = {}

    def parse(self):
        log.info("Parsing demo header")
        for pos, entry in enumerate(self.parse_demo_header()):
            self.header[self.DEMO_HEADER_FIELDS[pos]] = entry

        while 1:
            # Read a command header
            cmd, tick, slot = self.parse_command_header()
            log.debug("cmd header: %s, %s, %s", cmd, tick, slot)

            # If this is a stop command, just quit out
            if cmd == Command.CMD_STOP:
                log.info("Hit stop command")
                break
            elif cmd in self.DATA_COMMANDS:
                self.parse_data_packet()
            elif cmd == Command.CMD_USERCMD:
                self.parse_usercmd_packet()
            elif cmd in (Command.CMD_SIGNON, Command.CMD_PACKET):
                self.parse_demo_packet()

    def parse_demo_header(self):
        header_struct = struct.Struct(self.DEMO_HEADER_STRUCT_FMT)
        header_data = header_struct.unpack_from(
            self.data.read(struct.calcsize(self.DEMO_HEADER_STRUCT_FMT)), 0)
        return map(lambda i: i.rstrip('\0') if isinstance(i, str) else i, header_data)

    def parse_command_header(self):
        cmd = self.read_single_struct("B")

        log.debug("Found cmd %s", cmd)
        if cmd <= 0:
            return Command.CMD_STOP, 0, 0

        tick = self.read_single_struct("i")
        slot = self.read_single_struct("B")

        return cmd, tick, slot

    def parse_data_packet(self):
        size = self.read_single_struct("@i")
        if size <= 0:
            return ""

        data = self.data.read(size)
        return data

    def parse_usercmd_packet(self):
        outgoing = self.read_single_struct("i")
        data = self.parse_data_packet()
        return data, outgoing

    def parse_demo_packet(self):
        cmd_info = self.read_single_struct("@iffffffffffffffffffiffffffffffffffffff")

        # Don't need these values
        seq_nr_in = self.read_single_struct("i")
        seq_nr_out = self.read_single_struct("i")

        data = self.parse_data_packet()
        self.parse_complex_packet(Buffer(data))

    def parse_complex_packet(self, buff):
        while buff.pos < buff.size():
            try:
                cmd = self.read_int32(buff)
                size = self.read_int32(buff)
                data = buff.read(size)
                print cmd
            except:
                print "Had to break :("
                break

    def read_int32(self, buff):
        b, count, result = 0, 0, 0
        cont = True

        while cont:
            if count == 5:
                return result

            b = self.read_single_struct("B", buff)
            result |= (b & 0x7F) << (7 * count)
            count += 1
            cont = b & 0x80

        return result

    def read_single_struct(self, fmt, buff=None):
        buff = buff or self.data

        size = struct.calcsize(fmt)
        st = struct.Struct(fmt)

        return st.unpack_from(buff.read(size), 0)[0]


