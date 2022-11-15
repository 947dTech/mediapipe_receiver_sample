# -*- coding:utf-8 -*-

import json

import math
import numpy as np


def dict_to_np(dc, aspect_ratio=1.0):
    np_pos = np.asanyarray(
        [(dc["x"] - 0.5) / aspect_ratio,
         dc["y"] - 0.5,
         dc["z"] / aspect_ratio])
    return np_pos


def dict_to_world_np(dc):
    np_pos = np.asanyarray([dc["x"], dc["y"], dc["z"]])
    return np_pos


def dict_to_landmark(dc, aspect_ratio=1.0):
    np_pos = dict_to_np(dc, aspect_ratio=aspect_ratio)
    visibility = dc["visibility"] if "visibility" in dc else 0
    presence = dc["presence"] if "presence" in dc else 0
    return (np_pos, visibility, presence)


def dict_to_world_landmark(dc):
    np_pos = dict_to_world_np(dc)
    visibility = dc["visibility"] if "visibility" in dc else 0
    presence = dc["presence"] if "presence" in dc else 0
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


def world_landmark_list(dict_list):
    point_list = []
    visibility_list = []
    presence_list = []
    for dc in dict_list:
        point, visibility, presence = dict_to_world_landmark(dc)
        point_list.append(point)
        visibility_list.append(visibility)
        presence_list.append(presence)
    return (point_list, visibility_list, presence_list)
