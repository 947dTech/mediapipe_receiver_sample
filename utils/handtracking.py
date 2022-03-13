# -*- coding:utf-8 -*-

import json

import math
import numpy as np

def hand_rotation(point_list):
    # in both hand Z axis is pinky -> thumb direction
    side_vector = point_list[5] - point_list[17]

    # in both hand Y axis is finger -> wrist direction
    fingers_root_center = np.mean(
        [
            point_list[5],
            point_list[9],
            point_list[13],
            point_list[17],
        ], axis=0)
    dir_vector = point_list[0] - fingers_root_center
    dir_vector /= np.linalg.norm(dir_vector)

    # X = Z x Y
    # NOTE: in UE4 all coords are left-hand
    normal_vector = np.cross(side_vector, dir_vector)
    normal_vector /= np.linalg.norm(normal_vector)

    # recalc Z = X x Y
    z_vector = np.cross(normal_vector, dir_vector)
    hand_rot = np.eye(3)

    # print(normal_vector)
    # print(dir_vector)
    # print(z_vector)
    hand_rot[:3, 0] = normal_vector
    hand_rot[:3, 1] = dir_vector
    hand_rot[:3, 2] = z_vector

    return hand_rot
