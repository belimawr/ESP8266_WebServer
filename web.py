import socket

__version__ = '0.1'


class Request:
    def __init__(self):
        self.path = ''
        self.method = ''
        self.body = None
        self.headers = {}


class HTTPServer:
    def __init__(self, port=None, timeout=None, debug=False):
        self._port = port or 80
        self._timeout = timeout
        self._addr = '0.0.0.0'
        self._socket = socket.socket()
        self._current_request = None
        self._DEBUG = debug

    def serve_forever(self):
        try:
            self._start_web_server()
        except KeyboardInterrupt:
            self._debug('Closing socket...')
            self._socket.close()
            self.__init__(self._port, self._timeout, self._debug)
            self._debug('Good Bye ;)')

    def _start_web_server(self):
        self._socket.bind((self._addr, self._port))
        self._socket.settimeout(self._timeout)
        self._socket.listen(1)
        self._debug('Listening for requests on port:', self._port)

        while True:
            cl, addr = self._socket.accept()
            cl_file = cl.makefile('rwb')
            status = 200
            try:
                self._parse_request(cl_file)
            except Exception as e:
                status = 500
                print('Internal server error:', e)
            response = 'HTTP/1.0 %s' % status
            cl.send(response)
            cl.close()

    def _parse_request(self, cl_file):
        request = Request()

        # Reads the first line
        line = cl_file.readline()
        line = line.decode('utf8')

        # Parse the line and get the method and path
        split_line = line.split(' ')
        request.method = split_line[0]
        request.path = split_line[1]

        self._parse_headers(request, cl_file)
        self._parse_body(request, cl_file)
        self._debug('***********************************')
        self._debug(request.method.upper())
        self._debug(request.path)
        self._debug(request.headers)
        self._debug(request.body)
        self._debug('***********************************')
        self._debug('Waiting for another request...')

    def _parse_headers(self, request, cl_file):
        while True:
            line = cl_file.readline()
            line = line.decode('utf8')

            # If line is a blank line, the headers ended
            # and ther might be a body
            if line == '\r\n' or line == '\n':
                break

            # Actually parse the header line
            # On the format:
            # Header_name: Header_value
            try:
                split_line = line.split(':')
                k = split_line[0].rstrip().lstrip()
                v = split_line[1].rstrip().lstrip()
                request.headers[k] = v
            except Exception:
                print('Error parsing "%s"' % line)


    def _parse_body(self, request, cl_file):
        if request.headers.get('Content-Length'):
            length = int(request.headers.get('Content-Length'))
            request.body = cl_file.read(length)

    def _debug(self, *args, **kwargs):
        if self._DEBUG:
            print(*args, **kwargs)
