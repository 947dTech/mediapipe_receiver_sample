#!/usr/bin/env python

## @brief send json offline file, saved via json_dump.py

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
parser.add_argument("-i", type=str, help="file name", default="data.json")
args = parser.parse_args(sys.argv[1:])

host = args.t
port = args.p

data_list = []

files = []

if os.path.isdir(args.i):
    ipath = pathlib.Path(args.i)
    files = list(map(str, ipath.glob("*.json")))
elif os.path.isfile(args.i):
    files.append(args.i)
else:
    print("%s: no such file or directory", args.i)
    sys.exit(0)

for filename in files:
    print("reading file " + filename)
    with open(filename, "r") as f:
        data_list.append(json.load(f))

sleeptimes = []
timestart = data_list[0]["pose_landmarks_stamp"] * 1e-6
for dict_msg in data_list[1:]:
    timeend = dict_msg["pose_landmarks_stamp"] * 1e-6
    sleeptimes.append(timeend - timestart)
    timestart = timeend
sleeptimes.append(1.0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        for (dict_msg, sptime) in zip(data_list, sleeptimes):
            json_msg = json.dumps(dict_msg)

            # print("send: \"%s\" to %s:%d" % (json_msg, host, port))
            sock.sendto(json_msg.encode("utf-8"), (host, port))
            time.sleep(sptime)
except KeyboardInterrupt:
    sock.close()
