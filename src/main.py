#!/usr/bin/env python

# Copyright 2014 Mitchell Kember. Subject to the MIT License.

import argparse
import os
import sys

from scribbler.server import Server

# Description for the usage message.
DESC = "Starts the Scribbler Bot server."

# All web resources are in the public folder.
PUBLIC = '../public'

# Requests for any paths other than these will 404.
WHITELIST = ['/', '/index.html', '/404.html', '/style.css', '/script.js']

# Configure the arguments.
parser = argparse.ArgumentParser(description=DESC)
parser.add_argument(
    '-n',
    '--nobrowser',
    action='store_true',
    help="don't open the browser"
)
parser.add_argument(
    '-s',
    '--host',
    type=str,
    default='localhost',
    help='serve on this host'
)
parser.add_argument(
    '-p',
    '--port',
    type=int,
    default=8080,
    help="serve on this port"
)

# Go to this directory to make the relative paths work.
script_dir = os.path.dirname(sys.argv[0])
if script_dir:
    os.chdir(script_dir)

# Start the server.
args = parser.parse_args()
server = Server(args.host, args.port, PUBLIC, WHITELIST)
server.start(not args.nobrowser)
server.stay_alive()
