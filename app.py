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
        if self.path == '/':
            self.path = '/index.html'  # serve index.html by default
            if not os.path.exists(served_directory + '/index.html'):
                self.create_index_html()
        try:
            # Try to open the requested file
            # Decode the URL path
            file_path = served_directory + unquote(self.path)
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.end_headers()

                # If the requested file is a Jinja template, render it
                if file_path.endswith('.html'):
                    template = env.get_template('index_template.html')
                    items = self.get_directory_content(file_path)
                    rendered_template = template.render(items=items)
                    self.wfile.write(rendered_template.encode('utf-8'))
                else:
                    # Otherwise, serve the file as usual
                    self.copyfile(f, self.wfile)
        except FileNotFoundError:
            # If the file is not found, return a 404 error
            self.send_error(404, "File Not Found: %s" % self.path)

    # Get directory content (folders and files)
    def get_directory_content(self, directory):
        items = []
        for item in os.listdir(served_directory):
            # Ignore folders starting with '.'
            if not item.startswith('.'):
                item_path = os.path.join(directory, item)
                item_type = 'directory' if os.path.isdir(item_path) else 'file'

                # item_type = 'directory' if os.path.isdir(os.path.join(served_directory, item)) else 'file'
                # items.append({'name': item, 'type': item_type, 'url': item})
                items.append({'name': item, 'type': item_type, 'url': item})
                # If item is a directory, recursively get its contents
                if os.path.isdir(item_path):
                    sub_items = self.get_directory_content(item_path)
                    items.extend(sub_items)

        return items

    # Create index.html if not available
    def create_index_html(self):
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