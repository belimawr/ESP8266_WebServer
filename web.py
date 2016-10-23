import socket

__version__ = '0.1'

class Request:
    def __init__(self):
        self.path = ''
        self.method = ''
        self.body = None
        self.headers = {}


class HTTPServer:
    def __init__(self, port=None, timeout=None):
        self._port = port or 80
        self._timeout = timeout or 100
        self._addr = '0.0.0.0'
        self._socket = socket.socket()
        self._current_request = None

    def start_web_server(self):
        self._socket.bind((self._addr, self._port))
        self._socket.settimeout(self._timeout)
        self._socket.listen(1)

        while True:
            cl, addr = self._socket.accept()
            cl_file = cl.makefile('rwb', addr)
            status = 200
            try:
                self.parse_request(cl_file)
            except Exception as e:
                status = 500
                print('Internal server error:', e)
            response = 'HTTP/1.0 %s' % status
            cl.send(response)
            cl.close()

    def parse_request(self, cl_file):
        request = Request()

        # Reads the first line
        line = cl_file.readline()
        line = line.decode('utf8')

        # Parse the line and get the method and path
        split_line = line.split(' ')
        request.method = split_line[0]
        request.path = split_line[1]

        # Parse the other lines
        # Those are the HEADER lines
        while True:
            line = cl_file.readline()
            line = line.decode('utf8')

            # This is a blank line, so the headers ended
            # and the body starts now
            if line == '\r\n' or line == '\n':
                break

            # Actually parse the header line
            try:
                split_line = line.split(':')
                k = split_line[0].rstrip().lstrip()
                v = split_line[1].rstrip().lstrip()
                request.headers[k] = v
            except Exception:
                print('Error parsing "%s"' % line)

        # Parse the Body, if there is any
        if request.headers.get('Content-Length'):
            request.body = cl_file.read(int(request.headers.get('Content-Length')))
        print('***********************************')
        print(request.method.upper())
        print(request.path)
        print(request.headers)
        print(request.body)
        print('***********************************')
        print('Waiting for another request...')

