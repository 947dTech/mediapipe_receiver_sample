import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils import (
    calc_hands_from_pose,
    calc_feet_from_pose,
    calc_elbows_from_pose,
    calc_knees_from_pose,
    calc_body_from_pose,
    calc_shoulders_from_pose,
    calc_thighs_from_pose
)
from .facetracking import FACE_CONNECTIONS


# common
def draw_line(ax, p0, p1, color="red"):
    xlist = [p0[0], p1[0]]
    ylist = [p0[1], p1[1]]
    zlist = [p0[2], p1[2]]
    ax.plot(xlist, ylist, zlist, "-", color=color)


def draw_coords(ax, pos, rot, scale=1.0):
    pos_x = pos + (scale * rot[:3, 0])
    draw_line(ax, pos, pos_x, color="red")
    pos_y = pos + (scale * rot[:3, 1])
    draw_line(ax, pos, pos_y, color="green")
    pos_z = pos + (scale * rot[:3, 2])
    draw_line(ax, pos, pos_z, color="blue")


# posetracking
def draw_pose(ax, point_list):
    # right arm
    draw_line(ax, point_list[11], point_list[13], color="red")
    draw_line(ax, point_list[13], point_list[15], color="red")
    draw_line(ax, point_list[15], point_list[17], color="red")
    draw_line(ax, point_list[15], point_list[19], color="red")
    draw_line(ax, point_list[17], point_list[19], color="red")
    draw_line(ax, point_list[15], point_list[21], color="red")

    # left arm
    draw_line(ax, point_list[12], point_list[14], color="blue")
    draw_line(ax, point_list[14], point_list[16], color="blue")
    draw_line(ax, point_list[16], point_list[18], color="blue")
    draw_line(ax, point_list[16], point_list[20], color="blue")
    draw_line(ax, point_list[18], point_list[20], color="blue")
    draw_line(ax, point_list[16], point_list[22], color="blue")

    # right leg
    draw_line(ax, point_list[23], point_list[25], color="red")
    draw_line(ax, point_list[25], point_list[27], color="red")
    draw_line(ax, point_list[27], point_list[29], color="red")
    draw_line(ax, point_list[27], point_list[31], color="red")
    draw_line(ax, point_list[29], point_list[31], color="red")

    # left leg
    draw_line(ax, point_list[24], point_list[26], color="blue")
    draw_line(ax, point_list[26], point_list[28], color="blue")
    draw_line(ax, point_list[28], point_list[30], color="blue")
    draw_line(ax, point_list[28], point_list[32], color="blue")
    draw_line(ax, point_list[30], point_list[32], color="blue")

    # face
    draw_line(ax, point_list[0], point_list[1], color="green")
    draw_line(ax, point_list[1], point_list[2], color="green")
    draw_line(ax, point_list[2], point_list[3], color="green")
    draw_line(ax, point_list[3], point_list[7], color="green")

    draw_line(ax, point_list[0], point_list[4], color="green")
    draw_line(ax, point_list[4], point_list[5], color="green")
    draw_line(ax, point_list[5], point_list[6], color="green")
    draw_line(ax, point_list[6], point_list[8], color="green")

    draw_line(ax, point_list[9], point_list[10], color="green")

    # center body
    shoulder_center = (point_list[11] + point_list[12]) * 0.5
    pelvis_center = (point_list[23] + point_list[24]) * 0.5
    draw_line(ax, shoulder_center, pelvis_center, color="gray")

    # coordinates
    (shoulder_pos, shoulder_rot,
     pelvis_pos, pelvis_rot) = calc_body_from_pose(
         point_list)
    if shoulder_rot is not None:
        draw_coords(ax, shoulder_pos, shoulder_rot, scale=0.1)
    if pelvis_rot is not None:
        draw_coords(ax, pelvis_pos, pelvis_rot, scale=0.1)

    (l_upperarm_pos, l_upperarm_rot,
     r_upperarm_pos, r_upperarm_rot) = calc_shoulders_from_pose(
         point_list)
    if l_upperarm_rot is not None:
        draw_coords(ax, l_upperarm_pos, l_upperarm_rot, scale=0.1)
    if r_upperarm_rot is not None:
        draw_coords(ax, r_upperarm_pos, r_upperarm_rot, scale=0.1)

    (l_thigh_pos, l_thigh_rot,
     r_thigh_pos, r_thigh_rot) = calc_thighs_from_pose(
         point_list)
    if l_thigh_rot is not None:
        draw_coords(ax, l_thigh_pos, l_thigh_rot, scale=0.1)
    if r_thigh_rot is not None:
        draw_coords(ax, r_thigh_pos, r_thigh_rot, scale=0.1)

    (left_hand_pos, left_hand_rot,
     right_hand_pos, right_hand_rot) = calc_hands_from_pose(
        point_list)
    draw_coords(ax, left_hand_pos, left_hand_rot, scale=0.1)
    draw_coords(ax, right_hand_pos, right_hand_rot, scale=0.1)

    (left_foot_pos, left_foot_rot,
     right_foot_pos, right_foot_rot) = calc_feet_from_pose(
        point_list)
    draw_coords(ax, left_foot_pos, left_foot_rot, scale=0.1)
    draw_coords(ax, right_foot_pos, right_foot_rot, scale=0.1)

    # elbow, kneeは特異点になった場合upperarm, thighから回転のみ移植する
    (left_elbow_pos, left_elbow_rot,
     right_elbow_pos, right_elbow_rot) = calc_elbows_from_pose(
        point_list)
    if left_elbow_rot is None:
        if l_upperarm_rot is not None:
            draw_coords(ax, left_elbow_pos, l_upperarm_rot, scale=0.1)
    else:
        draw_coords(ax, left_elbow_pos, left_elbow_rot, scale=0.1)
    if right_elbow_rot is None:
        if r_upperarm_rot is not None:
            draw_coords(ax, right_elbow_pos, r_upperarm_rot, scale=0.1)
    else:
        draw_coords(ax, right_elbow_pos, right_elbow_rot, scale=0.1)

    (left_knee_pos, left_knee_rot,
     right_knee_pos, right_knee_rot) = calc_knees_from_pose(
        point_list)
    if left_knee_rot is None:
        if l_thigh_rot is not None:
            draw_coords(ax, left_knee_pos, l_thigh_rot, scale=0.1)
    else:
        draw_coords(ax, left_knee_pos, left_knee_rot, scale=0.1)
    if right_knee_rot is None:
        if r_thigh_rot is not None:
            draw_coords(ax, right_knee_pos, r_thigh_rot, scale=0.1)
    else:
        draw_coords(ax, right_knee_pos, right_knee_rot, scale=0.1)


# face tracking
def draw_face(ax, point_list, color="green"):
    for conns in FACE_CONNECTIONS:
        draw_line(ax, point_list[conns[0]], point_list[conns[1]], color=color)


# hand tracking
def draw_hand(ax, point_list, center=np.asanyarray([0, 0, 0]), color="red"):
    # thumb
    draw_line(ax, point_list[0] + center, point_list[1] + center, color=color)
    draw_line(ax, point_list[1] + center, point_list[2] + center, color=color)
    draw_line(ax, point_list[2] + center, point_list[3] + center, color=color)
    draw_line(ax, point_list[3] + center, point_list[4] + center, color=color)

    # index
    draw_line(ax, point_list[0] + center, point_list[5] + center, color=color)
    draw_line(ax, point_list[5] + center, point_list[6] + center, color=color)
    draw_line(ax, point_list[6] + center, point_list[7] + center, color=color)
    draw_line(ax, point_list[7] + center, point_list[8] + center, color=color)

    # middle
    draw_line(ax, point_list[0] + center, point_list[9] + center, color=color)
    draw_line(ax, point_list[9] + center, point_list[10] + center, color=color)
    draw_line(ax, point_list[10] + center, point_list[11] + center, color=color)
    draw_line(ax, point_list[11] + center, point_list[12] + center, color=color)

    # ring
    draw_line(ax, point_list[0] + center, point_list[13] + center, color=color)
    draw_line(ax, point_list[13] + center, point_list[14] + center, color=color)
    draw_line(ax, point_list[14] + center, point_list[15] + center, color=color)
    draw_line(ax, point_list[15] + center, point_list[16] + center, color=color)

    # pinky
    draw_line(ax, point_list[0] + center, point_list[17] + center, color=color)
    draw_line(ax, point_list[17] + center, point_list[18] + center, color=color)
    draw_line(ax, point_list[18] + center, point_list[19] + center, color=color)
    draw_line(ax, point_list[19] + center, point_list[20] + center, color=color)
