#!/usr/bin/env python3

import sys
import os
import socket
import time
from argparse import ArgumentParser
import json

parser = ArgumentParser()
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
parser.add_argument("-o", type=str, help="output filename", default="mediapipe_record.dat")
parser.add_argument("-d", type=int, help="duration", default=0)
parser.add_argument("-n", type=int, help="frames", default=1)
args = parser.parse_args(sys.argv[1:])

host = ""  # empty for receiver
port = args.p

filename = args.o

if args.d > 0:
    print("reciever will starts at %d seconds later." % (args.d))
    time.sleep(args.d)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
print("reciever active in port No. %d" % port)

f = open(filename, "w")


def write_frame(sock, f):
    msg, sender = sock.recvfrom(65536)
    json_msg = msg.decode(encoding="utf-8")
    f.write(json_msg)
    f.write("\n")


frame_count = 0
try:
    if args.n > 0:
        for i in range(args.n):
            write_frame(sock, f)
            frame_count += 1
    else:
        while True:
            write_frame(sock, f)
            frame_count += 1
    print("end frame.")
except KeyboardInterrupt:
    print("keyboard interrupted.")
finally:
    f.close()
    print("%d frame(s) are written." % frame_count)
