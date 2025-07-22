from Exscript.protocols.telnetlib import Telnet

from pymudclient import shared_data
from pymudclient.utils.colors import color_convert
from pymudclient.utils.print import (
    color_print,
    replace_line_print,
)


class TelnetClient:

    def __init__(self, host, port, encoding='latin1'):
        self.tn = Telnet(host, port)
        self.encoding = encoding

    def read_very_eager(self):
        return self.tn.read_very_eager()

    def re_decode(self, data):
        return data.encode('latin1').decode(self.encoding)

    def write(self, data):
        return self.tn.write(data.encode(self.encoding))

    def close(self):
        self.tn.close()


def send_to_host(text):
    try:
        if text != '':
            replace_line_print(f'$HIM$Send: {text}')
        shared_data.TN.get().write(text + '\r\n')

    except BrokenPipeError as err:
        color_print(f'$HIR$Sent to host error: {err}$NOR$')
        exit(color_convert('$HIR$Program was interrupted$NOR$'))
