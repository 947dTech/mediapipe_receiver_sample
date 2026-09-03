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

from utils import (
    draw_face,
    draw_hand,
    draw_pose,
    holistic_list,
)


parser = ArgumentParser()
parser.add_argument("-p", type=int, help="port No.", default=0x947d)
parser.add_argument("--draw", action="store_true", help="draw result, [NOTE] heavy process")
args = parser.parse_args(sys.argv[1:])

host = ""  # empty for receiver
port = args.p

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))
print("receiver active in port No. %d" % port)

if args.draw:
    fig = plt.figure(figsize=plt.figaspect(1))
    ax = fig.add_subplot(projection="3d")
    ax.grid()

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

prev_timestamp = time.clock_gettime_ns(time.CLOCK_MONOTONIC)

try:
    while True:
        msg, sender = sock.recvfrom(65536)
        json_msg = msg.decode(encoding="utf-8")
        dict_msg = json.loads(json_msg)

        if args.draw:
            ax.cla()

        print("--------------------------------")
        print("local time: %f" % time.time())

        (pose_list, pose_stamp,
         pose_world_list, pose_world_stamp,
         face_list, face_blendshapes, face_stamp,
         right_hand_list, right_hand_stamp,
         right_hand_world_list, right_hand_world_stamp,
         left_hand_list, left_hand_stamp,
         left_hand_world_list, left_hand_world_stamp) = holistic_list(dict_msg)

        if pose_list is None:
            print("  no data.")
            continue

        print("  pose stamp (base time): %f" % pose_stamp)
        print(f"  pose: {len(pose_list[0])} points")

        if pose_world_list is not None:
            print(f"  pose(3D): {len(pose_world_list[0])} points")
            if args.draw:
                draw_pose(ax, pose_world_list[0])
        else:
            print("  pose(3D): no data")

        if face_list is not None:
            print(f"  face: {len(face_list[0])} points")
            if args.draw:
                if len(face_list[0]) >= 468:
                    draw_face(ax, face_list[0])
            if face_blendshapes is not None:
                print("    with face_blendshapes")
        else:
            print("  face: no data")

        if right_hand_list is not None:
            print(f"  right_hand: {len(right_hand_list[0])} points")
        else:
            print("  right_hand: no data")

        if right_hand_world_list is not None:
            print(f"  right_hand(3D): {len(right_hand_world_list[0])} points")
            if args.draw:
                if len(right_hand_world_list[0]) == 21:
                    draw_hand(ax, right_hand_world_list[0], center=right_hand_world_list[0][0])
        else:
            print("  right_hand(3D): no data")

        if left_hand_list is not None:
            print(f"  left_hand: {len(left_hand_list[0])} points")
        else:
            print("  left_hand: no data")

        if left_hand_world_list is not None:
            print(f"  left_hand(3D): {len(left_hand_world_list[0])} points")
            if args.draw:
                if len(left_hand_world_list[0]) == 21:
                    draw_hand(ax, left_hand_world_list[0], center=left_hand_world_list[0][0])
        else:
            print("  left_hand(3D): no data")

        if args.draw:
            ax.set_xlim([-1.0, 1.0])
            ax.set_ylim([-1.0, 1.0])
            ax.set_zlim([-1.0, 1.0])
            plt.pause(0.001)

        print("fps: ", 1e9 / (pose_stamp - prev_timestamp))
        prev_timestamp = pose_stamp

except KeyboardInterrupt:
    sock.close()
except Exception as e:
    print(e)
