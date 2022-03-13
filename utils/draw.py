import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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
