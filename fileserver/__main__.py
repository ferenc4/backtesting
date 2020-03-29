#!/usr/bin/env python3
import functools
import socketserver
import sys
from http.server import SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


def run(port):
    httpd = socketserver.TCPServer(("", port), functools.partial(CORSRequestHandler, directory="public"))
    print("Serving HTTP on 0.0.0.0 port ", port)
    httpd.serve_forever()


if __name__ == '__main__':
    run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
