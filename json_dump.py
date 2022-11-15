#!/usr/bin/env python3

import sys
import os
import socket
import time
from argparse import ArgumentParser
import json

import math
import numpy as np

parser = ArgumentParser()
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
parser.add_argument("-o", type=str, help="output directory", default="data")
parser.add_argument("-d", type=int, help="duration", default=0)
parser.add_argument("-n", type=int, help="frames", default=1)
args = parser.parse_args(sys.argv[1:])

host = ""  # empty for receiver
port = args.p

dirname = args.o

if not os.path.exists(dirname):
    os.mkdir(dirname)

if args.d > 0:
    print("reciever will starts at %d seconds later." % (args.d))
    time.sleep(args.d)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
print("reciever active in port No. %d" % port)

for i in range(args.n):
    msg, sender = sock.recvfrom(65536)
    json_msg = msg.decode(encoding="utf-8")
    filename = "%s/%03d.json" % (dirname, i)
    with open(filename, "w") as f:
        f.write(json_msg)
