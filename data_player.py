#!/usr/bin/env python

import sys
import socket
import time
import random
from argparse import ArgumentParser
import json
import os
import pathlib

parser = ArgumentParser()
parser.add_argument("-t", type=str, help="target IP addr", default="127.0.0.1")
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
parser.add_argument("-i", type=str, help="file name", default="mediapipe_record.dat")
args = parser.parse_args(sys.argv[1:])

host = args.t
port = args.p

data_list = []

data_file = None

if os.path.isfile(args.i):
    data_file = args.i
else:
    print("%s: no such file or directory", args.i)
    sys.exit(0)

print("reading file " + data_file)
sleeptimes = []
with open(data_file, "r") as f:
    data = json.loads(f.readline())
    timestart = data["pose_landmarks_stamp"] * 1e-6
    while line := f.readline():
        data = json.loads(line)
        timeend = data["pose_landmarks_stamp"] * 1e-6
        sleeptimes.append(timeend - timestart)
        timestart = timeend
    sleeptimes.append(1.0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    f = open(data_file, "r")
    while True:
        frame_count = 0
        while json_msg := f.readline():
            t0 = time.time()
            sock.sendto(json_msg.encode("utf-8"), (host, port))
            sptime = sleeptimes[frame_count]
            frame_count += 1
            t1 = time.time()
            dur = sptime - (t1 - t0)
            if dur > 0.0:
                time.sleep(dur)
            else:
                print("frame dropped!")
        f.seek(0)
except KeyboardInterrupt:
    pass
finally:
    sock.close()
    f.close()
