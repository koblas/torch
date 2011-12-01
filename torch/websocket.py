import socket
import urlparse
from tornado import ioloop, iostream

class Connection(object):
    def __init__(self, host, port, io_loop=None, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.io_loop = io_loop
        self.stream = None

    def connect(self, callback=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        if self.timeout:
            s.setttimeout(self.timeout)
        s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.stream = iostream.IOStream(s, io_loop=self.io_loop)
        self.stream.connect((self.host, self.port), callback)

    def disconnet(self):
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
            self.stream = None

    def write(self, data):
        return self.stream.write(data)

    def read_until(self, endln, callback):
        return self.stream.read_until(endln, callback)

    def read_bytes(self, count, callback):
        return self.stream.read_until(count, callback)

class WebSocketClient(object):
    FRAME_START = '\x00'
    FRAME_END   = '\xff'

    def __init__(self, url, on_open=None, on_message=None, on_close=None, io_loop=None, timeout=None, **kwargs):
        self.url = url

        p = urlparse.urlparse(url)

        if p.hostname:
            host = p.hostname
        else:
            raise ValueError("Missing Hostname in URL")

        if p.scheme == 'ws':
            port = p.port or 80
        else:
            raise ValueError("Unsupported websocket protocol %s" % p.scheme)

        if port != 80:
            self.netloc = "%s:%s" % (host, port)
        else:
            self.netloc = host

        u = p.path or '/'
        if p.query:
            u += '?' + p.query
        self.http_url = u

        self.connection = Connection(host, port, io_loop=io_loop, timeout=timeout)

        self.on_message = on_message
        self.on_open    = on_open
        self.on_close   = on_close

    def connect(self):
        self.connection.connect(self._on_connect)
        return self

    def _on_connect(self):
        headers = {
            'Upgrade'    : 'WebSocket',
            'Connection' : 'Upgrade',
            'Host'       : self.netloc,
            'Origin'     : 'http://' + self.netloc,
        }

        self.connection.write("GET %s HTTP/1.1\r\n%s\r\n\r\n" % (
                                    self.http_url, 
                                    "\r\n".join(["%s: %s" % (k, v) for k, v in headers.items()])
                                ))

        self.headers = []
        self.headers_dict = {}
        self.connection.read_until("\r\n", self._handle_header_start)

    def _handle_header_start(self, header):
        # HTTP/1.1 101 Web Socket Protocol Handshake
        proto, status, rest = header.split(' ', 2)
        if proto != 'HTTP/1.1' or status != '101':
            raise Exception("Ack!")
        self.connection.read_until("\r\n", self._handle_header_line)

    def _handle_header_line(self, header):
        if header == '\r\n':
            return self._handle_header()
        k, v = header.split(':', 1)
        self.headers.append((k.strip(), v.strip()))
        self.headers_dict[k.strip().lower()] = v.strip()
        self.connection.read_until("\r\n", self._handle_header_line)

    def _handle_header(self):
        if self.headers_dict.get('connection', '').lower() != 'upgrade' or self.headers_dict.get('upgrade', '').lower() != 'websocket':
            raise Exception("Couldn't complete connection")

        if self.on_open:
            self.on_open()
        self.connection.read_until(self.FRAME_END, self._on_data)

    def send(self, data):
        self.connection.write(self.FRAME_START + data.encode('utf-8') + self.FRAME_END)

    def close(self):
        self.connection.close()

    def _on_data(self, data):
        if data[0] != self.FRAME_START or data[-1] != self.FRAME_END:
            raise Exception("Bad data")
        if self.on_message:
            self.on_message(data[1:-1])
        self.connection.read_until(self.FRAME_END, self._on_data)
