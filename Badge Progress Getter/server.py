from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        with open("badgesprogress.json", "r") as f:
            s = json.load(f)
            self.wfile.write(json.dumps(s).encode("utf8"))




def run(server_class=HTTPServer, handler_class=Server, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print("Opening server at port {}".format(port))
    httpd.serve_forever()


if __name__ == "__main__":
    run()
