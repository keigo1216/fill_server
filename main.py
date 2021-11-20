#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import annealing

class MyHandler(BaseHTTPRequestHandler):

    def make_response(self, response):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseBody = json.dumps(response)

        self.wfile.write(responseBody.encode('utf-8'))

    def error_response(self, e):
        print(type(e))
        print(e.args)
        print(e)
        response = { 'status' : 500, 'msg' : "'"+e.args+"'" }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        responseBody = json.dumps(response)

        self.wfile.write(responseBody.encode('utf-8'))

    def do_POST(self):
        print("receive POST request")
        try:
            response = self.body()
            self.make_response(response)
        except Exception as e:
            self.error_response(e)

    def do_GET(self):
        print("receive GET request")
        try:
            response = self.body()
            self.make_response(response)
        except Exception as e:
            self.error_response(e)

    def body(self):
        print("called body")
        result = annealing.app_body()
        print("result", result)
        response = { 'status' : 200, 'result' : result}
        return response

def importargs():
    parser = argparse.ArgumentParser("This is the simple server")

    parser.add_argument('--host', '-H', required=False, default='0.0.0.0')
    parser.add_argument('--port', '-P', required=False, type=int, default=8080)

    args = parser.parse_args()

    return args.host, args.port

def run(server_class=HTTPServer, handler_class=MyHandler, server_name='0.0.0.0', port=8080):

    server = server_class((server_name, port), handler_class)
    server.serve_forever()

def main():
    host, port = importargs()
    run(server_name=host, port=port)

if __name__ == '__main__':
    main()