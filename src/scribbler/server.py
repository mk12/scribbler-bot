# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements the server for the web application."""

import webbrowser
import os.path
import sys
import threading
import time
from wsgiref import simple_server

# ============================================================ 
#           Constants
# ============================================================ 

# Serve the website on port 8080.
PORT = 8080

# All HTML files and other resources are in the public folder.
PUBLIC = '../public'

# Requests for any files other than these will 404.
WHITELIST = ['/', '/index.html', '/404.html', '/style.css', '/script.js']

# Response statuses.
STATUS_200 = '200 OK'
STATUS_404 = '404 NOT FOUND'

# MIME types for file extensions.
MIME_PLAIN = 'text/plain'
MIMES = {'html': 'text/html', 'css': 'text/css', 'js': 'application/javascript'}

# Delay before opening the browser to give the server time to start up.
BROWSER_DELAY = 200

# ============================================================ 
#           Paths
# ============================================================ 

def relative_path(path_info):
    """Returns the relative path that should be followed for the request.
    Anything not present in the whitelist will cause a 404."""
    if path_info in WHITELIST:
        if path_info == '/':
            path_info = '/index.html'
    else:
        path_info = '/404.html'
    return PUBLIC + path_info

def get_status(path=None):
    """Returns the request status to use for the given path."""
    if path == '/404.html':
        return STATUS_404
    return STATUS_200

def get_mime(path=None):
    """Returns the MIME type to use for the given path. Defaults to 'text/plain'
    if the extension is not recognized, or if no argument is passed."""
    if not path:
        return MIME_PLAIN
    _, ext = os.path.splitext(path)
    without_dot = ext[1:]
    return MIMES.get(without_dot, MIME_PLAIN)

# ============================================================ 
#           GET and POST requests
# ============================================================ 

def headers(mime, length):
    """Returns a list of HTTP headers given the MIME type and the length of the
    content, in bytes (in integer or sting format)."""
    return [('Content-Type', mime),
            ('Content-Length', str(length))]

def handle_get(path_info, start_response):
    """Handles a GET request, which is used for getting resources."""
    path = relative_path(path_info)
    head = headers(get_mime(path), os.path.getsize(path))
    start_response(get_status(path), head)
    return open(path)

def handle_post(data, start_response):
    """Handles a POST request, which is used for AJAX communication."""
    msg = "received msg: {}".format(data)
    head = headers(get_mime(), len(msg))
    start_response(get_status(), head)
    # TODO: status => wait until status changes on different thread?
    return [msg]

def extract_data(environ):
    """Extracts the data from a POST request's environment."""
    try:
        length = int(environ.get('CONTENT_LENGTH', '0'))
    except ValueError:
        length = 0
    if length != 0:
        return environ['wsgi.input'].read(length)
    return ""

def handle_request(environ, start_response):
    """Handles a server request for the application."""
    method = environ['REQUEST_METHOD']
    if method == 'GET':
        path_info = environ['PATH_INFO']
        return handle_get(path_info, start_response)
    elif method == 'POST':
        data = extract_data(environ)
        return handle_post(data, start_response)

# ============================================================ 
#           Application
# ============================================================ 

def call_later(proc, delay):
    """Schedules `proc`, a function of no arguments, to be executed on a daemon
    thread after `delay` milliseconds. Returns immediately."""
    def delayed():
        time.sleep(delay / 1000.0)
        proc()
    t = threading.Thread(target=delayed)
    t.daemon = True
    t.start()

def open_browser():
    """Opens the web browser to the main page of the web application."""
    webbrowser.open('http://localhost:{}'.format(PORT))

def start_app():
    """Creates the web server and serves forever on the main thread. After a
    fixed delay, opens the web browser to the served page. Never returns. Exits
    when a keyboard interrupt (Control-C) is detected."""
    print("Starting the application...")
    httpd = simple_server.make_server('localhost', PORT, handle_request)
    print("Serving on port {}...".format(PORT))
    call_later(open_browser, BROWSER_DELAY)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit('Keyboard Interrupt')
