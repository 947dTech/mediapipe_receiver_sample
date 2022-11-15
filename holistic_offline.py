#!/usr/bin/env python

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
parser.add_argument("-r", type=float, help="aspect ratio", default=1.78)  # 1280/720
parser.add_argument("-i", type=str, help="file name", default="data.json")
args = parser.parse_args(sys.argv[1:])

# host = args.t
# host = ""  # empty for reciever
# port = args.p

# Pixel5:
# 1280 * 720, f = 895.4703369140625
image_width = 1280
image_height = 720
focal = 895.4703369140625

# aspect_ratio = args.r
aspect_ratio = float(image_width) / float(image_height)
filename = args.i
with open(filename, "r") as f:
    dict_msg = json.load(f)

# plot
fig = plt.figure(figsize=plt.figaspect(1))
ax = Axes3D(fig)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.set_xlim([-0.5, 0.5])
ax.set_ylim([-0.5, 0.5])
ax.set_zlim([-0.5, 0.5])

# convert to np list
(pose_list, pose_stamp,
    pose_world_list, pose_world_stamp,
    face_list, face_stamp,
    right_hand_list, right_hand_stamp,
    left_hand_list, left_hand_stamp) = utils.holistic_list(dict_msg, aspect_ratio=aspect_ratio)

# calc min/max
def min_max_points(landmark_list, label):
    if landmark_list is None:
        print("%s: not detected." % label)
    else:
        np_points = np.asanyarray(landmark_list[0])
        points_max = np.max(np_points, axis=0)
        points_min = np.min(np_points, axis=0)
        print("%s: range: %a - %a" % (label, points_min, points_max))


min_max_points(pose_list, "pose")
min_max_points(pose_world_list, "pose_world")
min_max_points(face_list, "face")
min_max_points(right_hand_list, "right_hand")
min_max_points(left_hand_list, "left_hand")

# points
pose_points = pose_list[0]
pose_world_points = pose_world_list[0]
if face_list is not None:
    face_points = face_list[0]
if right_hand_list is not None:
    right_hand_points = right_hand_list[0]
if left_hand_list is not None:
    left_hand_points = left_hand_list[0]

# calc uv (NOTE: before gravity)
pose_uvs = list(map(
    lambda x: np.array([
        x[0] * aspect_ratio * image_height,
        x[1] * image_width
    ]),
    pose_points))

uvarray = np.vstack(pose_uvs)
# print("uv range:")
# print(uvarray.max(axis=0), uvarray.min(axis=0))

# estimate hip position in camera coordinate
alist = []
blist = []
print("hip pos estimation:")
for uv, pt in zip(pose_uvs, pose_world_points):
    # print(uv[0] / image_width, uv[1] / image_height, pt)
    alist.append(np.array([focal, 0, -uv[0]]))
    alist.append(np.array([0, focal, -uv[1]]))
    blist.append(uv[0] * pt[2] - pt[0] * focal)
    blist.append(uv[1] * pt[2] - pt[1] * focal)
amat = np.vstack(alist)
bvec = np.asanyarray(blist)

# ainv = np.matmul(np.linalg.inv(np.matmul(amat.T, amat)), amat.T)
# hip_on_camera = np.matmul(ainv, bvec)
# print("hip_pos", hip_on_camera)
hip_on_camera = np.linalg.solve(np.matmul(amat.T, amat), np.matmul(amat.T, bvec))
print("hip_pos", hip_on_camera)

# gravity, in device coords
grav = np.asanyarray(dict_msg["gravity"])
print("grav: %a" % grav)
grav_accel = np.linalg.norm(grav)
print("grav accel: %f" % grav_accel)
ngrav = grav / grav_accel
# convert to camera coords
ngrav[1] = -ngrav[1]
ngrav[2] = -ngrav[2]

# create gravitated camera coords
gcamera_coords = np.eye(3)
gy_axis = -ngrav
slant = math.fabs(ngrav[2])
if slant > 0.6:
    print("invalid device pose. use raw data")
else:
    gx_axis = np.cross(gy_axis, np.asanyarray([0, 0, 1]))
    gx_axis /= np.linalg.norm(gx_axis)
    gz_axis = np.cross(gx_axis, gy_axis)
    grav_rot = np.eye(3)
    grav_rot[:3, 0] = gx_axis
    grav_rot[:3, 1] = gy_axis
    grav_rot[:3, 2] = gz_axis

    # transform all points
    grav_co = np.eye(4)
    grav_co[:3, :3] = grav_rot
    # grav_co[:3, 3] = pose_points[0]
    grav_co[:3, 3] = (pose_points[11] + pose_points[12]) * 0.5
    inv_grav_co = np.linalg.inv(grav_co)
    inv_grav_rot = inv_grav_co[:3, :3]
    inv_grav_trans = inv_grav_co[:3, 3]

    w_grav_co = np.eye(4)
    w_grav_co[:3, :3] = grav_rot
    # w_grav_co[:3, 3] = pose_world_points[0]
    w_grav_co[:3, 3] = (pose_world_points[11] + pose_world_points[12]) * 0.5
    inv_w_grav_co = np.linalg.inv(w_grav_co)
    inv_w_grav_rot = inv_w_grav_co[:3, :3]
    inv_w_grav_trans = inv_w_grav_co[:3, 3]

    hip_grav_co = np.eye(4)
    hip_grav_co[:3, :3] = grav_rot
    hip_grav_co[:3, 3] = -hip_on_camera  # 体から見たカメラ
    inv_hip_grav_co = np.linalg.inv(hip_grav_co)
    inv_hip_grav_rot = inv_hip_grav_co[:3, :3]
    inv_hip_grav_trans = inv_hip_grav_co[:3, 3]
    print("hip_pos (world): ", inv_hip_grav_trans)

    pose_points = list(map(lambda x: np.matmul(inv_grav_rot, x) + inv_grav_trans, pose_points))
    pose_world_points = list(map(lambda x: np.matmul(inv_w_grav_rot, x) + inv_w_grav_trans, pose_world_points))
    if face_list is not None:
        face_points = list(map(lambda x: np.matmul(inv_grav_rot, x) + inv_grav_trans, face_points))
    if right_hand_list is not None:
        right_hand_points = list(map(lambda x: np.matmul(inv_grav_rot, x) + inv_grav_trans, right_hand_points))
    if left_hand_list is not None:
        left_hand_points = list(map(lambda x: np.matmul(inv_grav_rot, x) + inv_grav_trans, left_hand_points))

# calc face/right/lefthand
if face_list is not None:
    nose_point = pose_points[0]
    nose_world_point = pose_world_points[0]
    print("nose pos: %a" % nose_point)
    print("nose pos (world): %a" % nose_world_point)

    lip_points = utils.extract_lip_points(face_points)
    lip_pos = np.mean(lip_points, axis=0)
    print("lip pos: %a" % lip_pos)

    right_eye_points = utils.extract_right_eye_points(face_points)
    right_eye_pos = np.mean(right_eye_points, axis=0)
    print("Reye pos: %a" % right_eye_pos)

    left_eye_points = utils.extract_left_eye_points(face_points)
    left_eye_pos = np.mean(left_eye_points, axis=0)
    print("Leye pos: %a" % left_eye_pos)

if right_hand_list is not None:
    right_hand_point = pose_world_points[16]
    right_hand_center = right_hand_point - right_hand_points[0]
    right_hand_rot = utils.hand_rotation(right_hand_points)
    print("Rhand pos: %a" % right_hand_point)
    print("Rhand rot:\n%a" % right_hand_rot)

if left_hand_list is not None:
    left_hand_point = pose_world_points[15]
    left_hand_center = left_hand_point - left_hand_points[0]
    left_hand_rot = utils.hand_rotation(left_hand_points)
    print("Lhand pos: %a" % left_hand_point)
    print("Lhand rot:\n%a" % left_hand_rot)


# plot
utils.draw_pose(ax, pose_world_points)
if face_list is not None:
    utils.draw_face(ax, face_points)
if right_hand_list is not None:
    utils.draw_hand(ax, right_hand_points, center=right_hand_center)
    utils.draw_coords(ax, right_hand_point, right_hand_rot, scale=0.1)
if left_hand_list is not None:
    utils.draw_hand(ax, left_hand_points, center=left_hand_center, color="blue")
    utils.draw_coords(ax, left_hand_point, left_hand_rot, scale=0.1)
plt.show()
