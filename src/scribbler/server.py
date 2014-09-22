# Copyright 2014 Mitchell Kember. Subject to the MIT License.

"""Implements the server for the web application."""

import webbrowser
from threading import Thread
from wsgiref.simple_server import make_server

PORT = 8080

def application(environ, start_response):
    """Handles server requests for the application."""
    if environ["REQUEST_METHOD"] == "POST":
    else:
        start_response("200 OK", [("Content-type", "text/html")])
        return "<html><body><h1>Hello World</h1></body></html>"

def open_browser():
    """Opens the web browser to the main page of the web app."""
    webbrowser.open("http://localhost:{}".format(PORT))

def start_app():
    """Creates the web server, starts it on another thread, opens the web
    browser to the served page, and then returns immediately."""
    httpd = make_server("", PORT, application)
    print("Serving on port {}...".format(PORT))
    Thread(target=httpd.serve_forever,daemon=True).start()
    open_browser("localhost:{}".format(PORT))
