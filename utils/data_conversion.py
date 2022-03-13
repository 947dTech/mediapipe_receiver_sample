# -*- coding:utf-8 -*-

import json

import math
import numpy as np

def dict_to_np(dc, aspect_ratio=1.0):
    np_pos = np.asanyarray([dc["x"] / aspect_ratio, dc["y"], dc["z"] / aspect_ratio])
    return np_pos

def dict_to_landmark(dc, aspect_ratio=1.0):
    np_pos = dict_to_np(dc, aspect_ratio=aspect_ratio)
    visibility = dc["visibility"]
    presence = dc["presence"]
    return (np_pos, visibility, presence)

def landmark_list(dict_list, aspect_ratio=1.0):
    point_list = []
    visibility_list = []
    presence_list = []
    for dc in dict_list:
        point, visibility, presence = dict_to_landmark(dc, aspect_ratio=aspect_ratio)
        point_list.append(point)
        visibility_list.append(visibility)
        presence_list.append(presence)
    return (point_list, visibility_list, presence_list)
