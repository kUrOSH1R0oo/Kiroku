from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Define the port and address for the server
server_address = ('', 8080)

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            keyboard_data = data.get('keyboardData', '')

            # Print or log the incoming keystrokes data
            print("Received data:", keyboard_data)

            # Respond with a status code 200 (OK)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'success'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': 'Invalid JSON'}
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server = server_class(server_address, handler_class)
    print(f'Starting server on port {server_address[1]}...')
    server.serve_forever()

if __name__ == "__main__":
    run()
