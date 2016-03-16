import BaseHTTPServer
import SimpleHTTPServer
import ssl
import sys

httpd = BaseHTTPServer.HTTPServer(('', int(sys.argv[3])),
                                  SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=sys.argv[1],
                               certfile=sys.argv[2], server_side=True)
httpd.serve_forever()
