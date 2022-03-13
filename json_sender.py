#!/usr/bin/env python3

## @brief send json offline file, saved via json_dump.py

import sys
import socket
import time
import random
from argparse import ArgumentParser
import json

parser = ArgumentParser()
parser.add_argument("-t", type=str, help="target IP addr", default="127.0.0.1")
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
parser.add_argument("-i", type=str, help="file name", default="data.json")
args = parser.parse_args(sys.argv[1:])

host = args.t
port = args.p

filename = args.i
with open(filename, "r") as f:
    dict_msg = json.load(f)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        json_msg = json.dumps(dict_msg)
        
        # print("send: \"%s\" to %s:%d" % (json_msg, host, port))
        sock.sendto(json_msg.encode("utf-8"), (host, port))
        time.sleep(1)
except KeyboardInterrupt:
    sock.close()
