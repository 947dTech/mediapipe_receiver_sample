# -*- coding:utf-8 -*-

import json

import math
import numpy as np

from .data_conversion import landmark_list

def holistic_list(dict_msg, aspect_ratio=1.0):
    pose_list = None
    pose_stamp = 0.0
    pose_world_list = None
    pose_world_stamp = 0.0
    face_list = None
    face_stamp = 0.0
    right_hand_list = None
    right_hand_stamp = 0.0
    left_hand_list = None
    left_hand_stamp = 0.0

    if "pose_landmarks" in dict_msg:
        pose_landmarks = dict_msg["pose_landmarks"]
        pose_stamp = dict_msg["pose_landmarks_stamp"]
        pose_list = landmark_list(pose_landmarks, aspect_ratio=aspect_ratio)

    if "pose_world_landmarks" in dict_msg:
        pose_world_landmarks = dict_msg["pose_world_landmarks"]
        pose_world_stamp = dict_msg["pose_world_landmarks_stamp"]
        pose_world_list = landmark_list(pose_world_landmarks, aspect_ratio=1.0)

    if "face_landmarks" in dict_msg:
        face_landmarks = dict_msg["face_landmarks"]
        face_stamp = dict_msg["face_landmarks_stamp"]
        face_list = landmark_list(face_landmarks, aspect_ratio=aspect_ratio)

    if "left_hand_landmarks" in dict_msg:
        left_hand_landmarks = dict_msg["left_hand_landmarks"]
        left_hand_stamp = dict_msg["left_hand_landmarks_stamp"]
        left_hand_list = landmark_list(left_hand_landmarks, aspect_ratio=aspect_ratio)

    if "right_hand_landmarks" in dict_msg:
        right_hand_landmarks = dict_msg["right_hand_landmarks"]
        right_hand_stamp = dict_msg["right_hand_landmarks_stamp"]
        right_hand_list = landmark_list(right_hand_landmarks, aspect_ratio=aspect_ratio)

    return (
        pose_list, pose_stamp,
        pose_world_list, pose_world_stamp,
        face_list, face_stamp,
        right_hand_list, right_hand_stamp,
        left_hand_list, left_hand_stamp)
