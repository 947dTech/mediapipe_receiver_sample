# -*- coding:utf-8 -*-

import json

import math
import numpy as np

from .data_conversion import dict_to_landmark


# @brief for old posetracking format
def posetracking_list_old(dict_msg, aspect_ratio=1.0):
    point_list = []
    visibility_list = []
    presence_list = []
    for i in range(33):
        dc = dict_msg[str(i)]
        point, visibility, presence = dict_to_landmark(dc, aspect_ratio=aspect_ratio)
        point_list.append(point)
        visibility_list.append(visibility)
        presence_list.append(presence)
    return (point_list, visibility_list, presence_list)


# body (shoulder and pelvis)
def calc_body_from_pose(pose_points):
    shoulder_center = (pose_points[11] + pose_points[12]) * 0.5
    shoulder_vec = pose_points[11] - pose_points[12]
    pelvis_center = (pose_points[23] + pose_points[24]) * 0.5
    pelvis_vec = pose_points[23] - pose_points[24]
    shoulder_to_pelvis = pelvis_center - shoulder_center

    shoulder_vec_legnth = np.linalg.norm(shoulder_vec)
    pelvis_vec_legnth = np.linalg.norm(pelvis_vec)
    shoulder_to_pelvis_length = np.linalg.norm(shoulder_to_pelvis)

    # NOTE: この計算が失敗するということは認識に失敗している
    if (shoulder_vec_legnth < 1e-5 and pelvis_vec_legnth < 1e-5 and shoulder_to_pelvis_length < 1e-5):
        return None, None, None, None

    shoulder_vec /= shoulder_vec_legnth
    pelvis_vec /= pelvis_vec_legnth
    shoulder_to_pelvis /= shoulder_to_pelvis_length

    shoulder_z = np.cross(shoulder_vec, shoulder_to_pelvis)
    pelvis_z = np.cross(pelvis_vec, shoulder_to_pelvis)

    shoulder_y = np.cross(shoulder_z, shoulder_vec)
    pelvis_y = np.cross(pelvis_z, pelvis_vec)

    shoulder_co = np.eye(3)
    shoulder_co[:3, 0] = shoulder_vec
    shoulder_co[:3, 1] = shoulder_y
    shoulder_co[:3, 2] = shoulder_z

    pelvis_co = np.eye(3)
    pelvis_co[:3, 0] = pelvis_vec
    pelvis_co[:3, 1] = pelvis_y
    pelvis_co[:3, 2] = pelvis_z

    return shoulder_center, shoulder_co, pelvis_center, pelvis_co


# forearms and thighs
def calc_limb_root_coordinate(pose_points, left_idx, right_idx):
    body_vec = pose_points[left_idx] - pose_points[right_idx]
    body_vec_legnth = np.linalg.norm(body_vec)
    l_limb_vec = pose_points[left_idx] - pose_points[left_idx + 2]
    l_limb_vec_length = np.linalg.norm(l_limb_vec)
    r_limb_vec = pose_points[right_idx] - pose_points[right_idx + 2]
    r_limb_vec_length = np.linalg.norm(r_limb_vec)

    shoulder_center = (pose_points[11] + pose_points[12]) * 0.5
    pelvis_center = (pose_points[23] + pose_points[24]) * 0.5
    shoulder_to_pelvis = pelvis_center - shoulder_center
    shoulder_to_pelvis_length = np.linalg.norm(shoulder_to_pelvis)

    # NOTE: この計算が失敗するということは認識に失敗している
    if (body_vec_legnth < 1e-5 and l_limb_vec_length < 1e-5 and r_limb_vec_length < 1e-5 and shoulder_to_pelvis_length < 1e-5):
        return None, None, None, None

    body_vec /= body_vec_legnth
    l_limb_vec /= l_limb_vec_length
    r_limb_vec /= r_limb_vec_length
    shoulder_to_pelvis /= shoulder_to_pelvis_length

    l_cos_angle = np.dot(body_vec, l_limb_vec)
    l_limb_co = np.eye(3)
    if math.fabs(l_cos_angle) > 1e-5:
        l_limb_z = np.cross(body_vec, l_limb_vec)
        l_limb_x = np.cross(l_limb_vec, l_limb_z)
    else:
        l_limb_x = shoulder_to_pelvis
        l_limb_z = np.cross(l_limb_x, l_limb_vec)
    l_limb_co[:3, 0] = l_limb_x
    l_limb_co[:3, 1] = l_limb_vec
    l_limb_co[:3, 2] = l_limb_z

    r_cos_angle = np.dot(body_vec, r_limb_vec)
    r_limb_co = np.eye(3)
    if math.fabs(r_cos_angle) > 1e-5:
        r_limb_z = np.cross(body_vec, r_limb_vec)
        r_limb_x = np.cross(r_limb_vec, r_limb_z)
    else:
        r_limb_x = shoulder_to_pelvis
        r_limb_z = np.cross(r_limb_x, r_limb_vec)
    r_limb_co[:3, 0] = r_limb_x
    r_limb_co[:3, 1] = r_limb_vec
    r_limb_co[:3, 2] = r_limb_z

    return pose_points[left_idx], l_limb_co, pose_points[right_idx], r_limb_co


def calc_shoulders_from_pose(pose_points):
    return calc_limb_root_coordinate(pose_points, 11, 12)


def calc_thighs_from_pose(pose_points):
    # return calc_limb_root_coordinate(pose_points, 23, 24)
    l_thigh_pos, l_thigh_co, r_thigh_pos, r_thigh_co = calc_limb_root_coordinate(pose_points, 23, 24)
    if l_thigh_co is not None:
        l_thigh_co[:3, 0] = -l_thigh_co[:3, 0]
        l_thigh_co[:3, 2] = -l_thigh_co[:3, 2]
    if r_thigh_co is not None:
        r_thigh_co[:3, 0] = -r_thigh_co[:3, 0]
        r_thigh_co[:3, 2] = -r_thigh_co[:3, 2]
    return l_thigh_pos, l_thigh_co, r_thigh_pos, r_thigh_co


# hands and feet
def calc_eef_coordinate(p0, p1, p2):
    dir_vec = p2 - p1
    dir_length = np.linalg.norm(dir_vec)
    root_vec = p0 - p1
    root_length = np.linalg.norm(root_vec)

    co = np.eye(3)
    # TODO: 計算できない場合はどうする？
    if dir_length > 1e-5 and root_length > 1e-5:
        z = dir_vec / dir_length
        x = np.cross(root_vec, z)
        x /= np.linalg.norm(x)
        y = np.cross(z, x)

        co[:3, 0] = x
        co[:3, 1] = y
        co[:3, 2] = z

    return co


def calc_hands_from_pose(pose_points):
    left_co = calc_eef_coordinate(
        pose_points[15], pose_points[17], pose_points[19])
    right_co = calc_eef_coordinate(
        pose_points[16], pose_points[18], pose_points[20])

    return (pose_points[15], left_co, pose_points[16], right_co)


def calc_feet_from_pose(pose_points):
    left_co = calc_eef_coordinate(
        pose_points[27], pose_points[29], pose_points[31])
    right_co = calc_eef_coordinate(
        pose_points[28], pose_points[30], pose_points[32])

    return (pose_points[27], left_co, pose_points[28], right_co)


# elbows and knees
def calc_middle_joint_coordinate(p0, p1, p2):
    v0 = p0 - p1
    v0_length = np.linalg.norm(v0)
    v1 = p1 - p2
    v1_length = np.linalg.norm(v1)

    co = None
    # TODO: 計算できない場合はどうする？
    # TODO: この方法だと、膝がy軸周りに反転してしまう。
    if v0_length > 1e-5 and v1_length > 1e-5:
        nv0 = v0 / v0_length
        y = v1 / v1_length
        cos_angle = np.dot(nv0, y)
        if (1.0 - math.fabs(cos_angle)) > 1e-5:
            co = np.eye(3)
            x = np.cross(y, nv0)
            x /= np.linalg.norm(x)
            z = np.cross(x, y)

            co[:3, 0] = x
            co[:3, 1] = y
            co[:3, 2] = z

    return co


def calc_elbows_from_pose(pose_points):
    left_co = calc_middle_joint_coordinate(
        pose_points[11], pose_points[13], pose_points[15])
    right_co = calc_middle_joint_coordinate(
        pose_points[12], pose_points[14], pose_points[16])

    return (pose_points[13], left_co, pose_points[14], right_co)


def calc_knees_from_pose(pose_points):
    left_co = calc_middle_joint_coordinate(
        pose_points[23], pose_points[25], pose_points[27])
    right_co = calc_middle_joint_coordinate(
        pose_points[24], pose_points[26], pose_points[28])

    # NOTE: 膝反転対策
    # ひとまずx,z軸を反転させる
    # TODO: 鳥足が出てきた場合は？
    # if left_co is not None:
    #     left_co[:3, 0] = -left_co[:3, 0]
    #     left_co[:3, 2] = -left_co[:3, 2]
    # if right_co is not None:
    #     right_co[:3, 0] = -right_co[:3, 0]
    #     right_co[:3, 2] = -right_co[:3, 2]

    return (pose_points[25], left_co, pose_points[26], right_co)
