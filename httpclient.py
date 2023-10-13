#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Anuj Pradeep
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
from urllib.parse import ParseResult, urlparse
# you may use urllib to encode data appropriately


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return "status code: {}\nbody: {}".format(self.code, self.body)


class HTTPClient(object):
    '''
        Returns the host, port, and path of the url
        If the path is empty, replace it with "/"
        If the port is None, depending on the scheme, use the default ones for it
    '''

    def get_host_port(self, url):
        results: ParseResult = urlparse(url)
        host = results.hostname
        path = results.path

        if path == "":
            path = "/"

        if (results.port == None):
            port = 443 if results.scheme == "https" else 80
        else:
            port = results.port

        return host, port, path

    '''
		Connect to a socket using the host and port
	'''

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    '''
		data is the response from the web server to our request
		returns the status code of the response, as an int
	'''

    def get_code(self, data: str):
        header = self.get_headers(data)
        return int(header.split("\n")[0].split(" ")[1])

    '''
		data is the response from the web server to our request
		returns the HTTP header of the response 
	'''

    def get_headers(self, data: str):
        return data.split("\r\n\r\n")[0]

    '''
		data is the response from the web server to our request
		returns the body of the response
	'''

    def get_body(self, data: str):
        return data.split('\r\n\r\n')[1]

    '''
		data is the request to the web server
		sends the request through the web server
	'''

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    '''
		Closes the socket
	'''

    def close(self):
        self.socket.close()

    '''
		receives the response from the server
	'''

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    '''
		handles a GET request given an url and returns the status code and the body from the response of the web server
	'''

    def GET(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)
        self.connect(host, port)
        
        # As mentioned in the Discussion board, args will be used for the query. You can also just put the query in the initial url and path will have that
        if args:
            path += "?"
            for key, value in args.items():
                path += f"{key}={value}&"

        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        self.sendall(request)

        data = self.recvall(self.socket)

        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    '''
		Handles a POST request given an url some arguments. Returns the status code and the body from the response of the web server
	'''

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, path = self.get_host_port(url)
        self.connect(host, port)

        temp = ""
        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\n"

        if args:
            for key, value in args.items():
                temp += f"{key}={value}&"
        request += f"Content-Length: {len(temp)}\r\n\r\n"
        request += temp
        self.sendall(request)

        data = self.recvall(self.socket)

        code = self.get_code(data)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)

    '''
		Handles whether the command is GET or POST when the script is invoked through command line
	'''

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[2]))
