'''
Created on

@author: Raja CSP Raman

source:
    ?
'''

import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from jinja2 import Environment, FileSystemLoader
from urllib.parse import unquote

# Set up Jinja environment
template_dir = 'templates'  # directory containing your Jinja templates
env = Environment(loader=FileSystemLoader(template_dir))

# Define the request handler class
class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    # Override do_GET method to render Jinja templates
    def do_GET(self):
        try:
            # if self.path == '/':
            #     self.path = '/index.html'  # serve index.html by default
            #     if not os.path.exists(served_directory + '/index.html'):
            #         self.create_index_html()
            file_path = served_directory + unquote(self.path)
            if os.path.isfile(file_path):
                self.serve_file(file_path)
            elif os.path.isdir(file_path):
                self.serve_directory(file_path)
            else:
                # Try to serve the file from subdirectories
                subdirectories = self.path.split('/')
                subdirectories = [d for d in subdirectories if d]  # Remove empty strings
                nested_path = served_directory
                for directory in subdirectories:
                    nested_path = os.path.join(nested_path, directory)
                    if not os.path.exists(nested_path):
                        self.send_error(404, "File Not Found: %s" % self.path)
                        return
                if os.path.isfile(nested_path):
                    self.serve_file(nested_path)
                else:
                    self.send_error(404, "File Not Found: %s" % self.path)
        except Exception as e:
            self.send_error(500, "Internal Server Error: %s" % str(e))

    def serve_file(self, file_path):
        # Serve the requested file
        with open(file_path, 'rb') as f:
            self.send_response(200)
            self.end_headers()
            self.copyfile(f, self.wfile)

    def serve_directory(self, directory):
        # Serve the directory listing
        items = self.get_directory_content(directory)
        template = env.get_template('index_template.html')
        rendered_template = template.render(items=items)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(rendered_template.encode('utf-8'))

    def get_directory_content(self, directory):
        # Get directory content (folders and files)
        items = []
        for item in os.listdir(directory):
            # Ignore folders starting with '.'
            if not item.startswith('.'):
                item_path = os.path.join(directory, item)
                item_type = 'directory' if os.path.isdir(item_path) else 'file'
                items.append({'name': item, 'type': item_type, 'url': item})
        return items

    def create_index_html(self):
        # Create index.html if not available
        with open(served_directory + '/index.html', 'w') as f:
            f.write('<!DOCTYPE html>\n<html>\n<head>\n<title>Index</title>\n</head>\n<body>\n<h1>Welcome to Index Page!</h1>\n</body>\n</html>')


    def server_close(self):
        # Cleanup the index.html file
        index_file_path = served_directory + '/index.html'
        if os.path.exists(index_file_path):
            os.remove(index_file_path)
        super().server_close()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="PyShare: Simple HTTP Server to share your local files to the world!")
parser.add_argument("folder", help="Folder path to serve")
args = parser.parse_args()

# Specify the directory you want to serve
served_directory = args.folder

# Define the server's host and port
host = '127.0.0.1'  # localhost
port = 8000

# Create an HTTP server instance
server = HTTPServer((host, port), MyHTTPRequestHandler)

# Start the server
# print(f"Server running on {host}:{port}")
# server.serve_forever()

try:
    # Start the server
    print(f"Server running on {host}:{port}")
    server.serve_forever()
except KeyboardInterrupt:
    # If interrupted, gracefully shutdown the server
    print("Bye!")
    server.server_close()