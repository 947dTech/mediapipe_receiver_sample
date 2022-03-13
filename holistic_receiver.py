#!/usr/bin/env python3

import sys
import socket
import time
from argparse import ArgumentParser
import json

import math
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import utils

parser = ArgumentParser()
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
args = parser.parse_args(sys.argv[1:])

host = ""  # empty for receiver
port = args.p

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
print("receiver active in port No. %d" % port)
    
try:
    while True:
        msg, sender = sock.recvfrom(65536)
        json_msg = msg.decode(encoding="utf-8")
        dict_msg = json.loads(json_msg)
        
        print("--------------------------------")
        print("local time: %f" % time.time())

        has_pose = "pose_landmarks_stamp" in dict_msg
        has_face = "face_landmarks_stamp" in dict_msg
        has_rhand = "right_hand_landmarks_stamp" in dict_msg
        has_lhand = "left_hand_landmarks_stamp" in dict_msg

        if not has_pose:
            print("  no data.")
            continue

        pose_stamp = dict_msg["pose_landmarks_stamp"]
        print("  pose stamp (base time): %f" % pose_stamp)

        face_stamp = 0.0
        face_stamp_delay = 0.0
        if has_face:
            face_stamp = dict_msg["face_landmarks_stamp"]
            face_stamp_delay = (face_stamp - pose_stamp)
            print("  face stamp : %f" % face_stamp)
            print("  face delay : %f" % face_stamp_delay)
        else:
            print("  face: no data")

        rhand_stamp = 0.0
        rhand_stamp_delay = 0.0
        if has_rhand:
            rhand_stamp = dict_msg["right_hand_landmarks_stamp"]
            rhand_stamp_delay = (rhand_stamp - pose_stamp)
            print("  rhand stamp : %f" % rhand_stamp)
            print("  rhand delay : %f" % rhand_stamp_delay)
        else:
            print("  rhand: no data")

        lhand_stamp = 0.0
        lhand_stamp_delay = 0.0            
        if has_lhand:
            lhand_stamp = dict_msg["left_hand_landmarks_stamp"]
            lhand_stamp_delay = (lhand_stamp - pose_stamp)
            print("  lhand stamp : %f" % lhand_stamp)
            print("  lhand delay : %f" % lhand_stamp_delay)
        else:
            print("  lhand: no data")
        
except KeyboardInterrupt:
    sock.close()
except Exception as e:
    print(e)
