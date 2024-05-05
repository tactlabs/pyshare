'''
Created on

@author: Raja CSP Raman

source:
    ?
'''

from http.server import SimpleHTTPRequestHandler, HTTPServer
import os
from jinja2 import Environment, FileSystemLoader

# Set up Jinja environment
template_dir = 'templates'  # directory containing your Jinja templates
env = Environment(loader=FileSystemLoader(template_dir))

# Specify the directory you want to serve
served_directory = '/home/rajaraman/csp/mlbooks'

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
            file_path = served_directory + self.path
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.end_headers()
                # If the requested file is a Jinja template, render it
                if file_path.endswith('.html'):
                    template = env.get_template('index_template.html')
                    items = self.get_directory_content()
                    rendered_template = template.render(items=items)
                    self.wfile.write(rendered_template.encode('utf-8'))
                else:
                    # Otherwise, serve the file as usual
                    self.copyfile(f, self.wfile)
        except FileNotFoundError:
            # If the file is not found, return a 404 error
            self.send_error(404, "File Not Found: %s" % self.path)

    # Get directory content (folders and files)
    def get_directory_content(self):
        items = []
        for item in os.listdir(served_directory):
            item_type = 'directory' if os.path.isdir(os.path.join(served_directory, item)) else 'file'
            items.append({'name': item, 'type': item_type, 'url': item})
        return items

# Define the server's host and port
host = '127.0.0.1'  # localhost
port = 8000

# Create an HTTP server instance
server = HTTPServer((host, port), MyHTTPRequestHandler)

# Start the server
print(f"Server running on {host}:{port}")
server.serve_forever()