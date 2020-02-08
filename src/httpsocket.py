from typing import Dict, List, Iterable, Tuple, Final, Union
from socket import socket, AF_INET, SOCK_STREAM


class HttpHeader:
    _header: Dict[str, List[str]] = {}

    def add(self, key: str, value: str):
        key = key.lower()
        if key not in self._header:
            self._header[key] = []
        self._header[key].append(value.lower())

    def items(self) -> Iterable[Tuple[str, str]]:
        for k, v in self._header.items():
            for e in v:
                yield k, e

    def merge(self, other: 'HttpHeader'):
        for k, v in other.items():
            self.add(k, v)

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._header

    def __getitem__(self, key: str) -> List[str]:
        return self._header[key.lower()]


class HttpRequest:
    _header: HttpHeader = HttpHeader()
    _body: bytes = b''
    _path: str = ''
    _method: str = ''
    _encoding: str = ''

    def __init__(self, path: str, method='GET',
                 header: HttpHeader = None, encoding='utf-8'):
        self._path = path
        self._method = method
        self._encoding = encoding
        if header:
            self._header = header

    def add_header(self, key: str, value: str) -> 'HttpRequest':
        self._header.add(key, value)
        return self

    def add_body(self, body: str) -> 'HttpRequest':
        self._body += body.encode(self._encoding)
        return self

    def to_bytes(self) -> bytes:
        buffer = b''

        def add_to_buffer(data: str):
            nonlocal buffer
            buffer += str.encode(self._encoding)

        add_to_buffer(f'{self._method} {self._path} HTTP/1.1\r\n')
        for k, v in self._header.items():
            add_to_buffer(f'{k}: {v}\r\n')
        length = len(self._body)
        if length > 0:
            add_to_buffer(f'content-length: {length}\r\n')
        add_to_buffer('\r\n')
        if length > 0:
            buffer += self._body
        return buffer


class HttpSocket:
    _host: str
    _port: int
    _socket: socket
    _encoding: str

    def __init__(self, host: str, port: int, encoding: str = 'utf-8'):
        self._host = host
        self._port = port
        self._encoding = encoding
        self._socket = socket(AF_INET, SOCK_STREAM)
        self._socket.connect((self._host, self._port))

    def url(self) -> str:
        return f"{self._host}:{self._port}"

    def close(self):
        self._socket.close()

    def write_bytes(self, buffer: bytes):
        self._socket.send(buffer)

    def write_str(self, string: str):
        self._socket.send(str.encode(self._encoding))

    def read_bytes(self, size: int) -> bytes:
        return self._socket.recv(size)

    def read_line(self) -> str:
        line, cur, next = b'', b'', b''
        while True:
            cur = self._socket.recv(1)
            if cur == b'\x0d':
                next = self._socket.recv(1)
                if next == b'\x0a':
                    break
                else:
                    line += cur
                    line += next
            else:
                line += cur
        return line.decode(self._encoding)

    def read_header(self) -> HttpHeader:
        header = HttpHeader()
        while True:
            line = self.read_line()
            if not line:
                break
            i = line.find(':')
            if i > 0:
                header.add(line[0:i].strip(), line[i+1:].strip())
        return header

    def read_body(self, header=None) -> str:
        if header == None:
            header = self.read_header()

        buffer = b''

        def read_to_buffer(size: int):
            nonlocal buffer
            while size > 0:
                buf = self.read_bytes(size)
                buffer += buf
                size -= len(buf)

        if 'Transfer-Encoding' in header and \
                'chunked' in header['Transfer-Encoding']:
            while True:
                length = int(self.read_line(), base=16)
                if length <= 0:
                    self.read_line()
                    break
                read_to_buffer(length)
                self.read_line()
        elif 'Content-Length' in header:
            length = int(header['Content-Length'][0], base=10)
            read_to_buffer(length)
        else:
            raise Exception('Unsupported transfer mode')

        return buffer.decode(self._encoding)

    def get_http(self, path: str, encoding='utf-8') -> str:
        request = HttpRequest(path, encoding=encoding)
        request.add_header("Host", self.url()) \
            .add_header("Connection", "keep-alive") \
            .add_header("Cache-Control", "max-age=0") \
            .add_header("Upgrade-Insecure-Requests", "1") \
            .add_header("User-Agent",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36") \
            .add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8") \
            .add_header("Accept-Encoding", "gzip, deflate") \
            .add_header("Accept-Language", "zh-CN,zh;q=0.9")
        self.write_bytes(request.to_bytes())
        return self.read_body()

    def __enter__(self):
        return self

    def __exit__(self, e_t, e_v, t_b):
        self.close()
