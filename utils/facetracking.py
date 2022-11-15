# -*- coding:utf-8 -*-

import json

import math
import numpy as np

import itertools

# from mediapipe/python/solutions/face_mesh.py
FACE_CONNECTIONS = frozenset([
    # Lips.
    (61, 146),
    (146, 91),
    (91, 181),
    (181, 84),
    (84, 17),
    (17, 314),
    (314, 405),
    (405, 321),
    (321, 375),
    (375, 291),
    (61, 185),
    (185, 40),
    (40, 39),
    (39, 37),
    (37, 0),
    (0, 267),
    (267, 269),
    (269, 270),
    (270, 409),
    (409, 291),
    (78, 95),
    (95, 88),
    (88, 178),
    (178, 87),
    (87, 14),
    (14, 317),
    (317, 402),
    (402, 318),
    (318, 324),
    (324, 308),
    (78, 191),
    (191, 80),
    (80, 81),
    (81, 82),
    (82, 13),
    (13, 312),
    (312, 311),
    (311, 310),
    (310, 415),
    (415, 308),
    # Left eye.
    (263, 249),
    (249, 390),
    (390, 373),
    (373, 374),
    (374, 380),
    (380, 381),
    (381, 382),
    (382, 362),
    (263, 466),
    (466, 388),
    (388, 387),
    (387, 386),
    (386, 385),
    (385, 384),
    (384, 398),
    (398, 362),
    # Left eyebrow.
    (276, 283),
    (283, 282),
    (282, 295),
    (295, 285),
    (300, 293),
    (293, 334),
    (334, 296),
    (296, 336),
    # Right eye.
    (33, 7),
    (7, 163),
    (163, 144),
    (144, 145),
    (145, 153),
    (153, 154),
    (154, 155),
    (155, 133),
    (33, 246),
    (246, 161),
    (161, 160),
    (160, 159),
    (159, 158),
    (158, 157),
    (157, 173),
    (173, 133),
    # Right eyebrow.
    (46, 53),
    (53, 52),
    (52, 65),
    (65, 55),
    (70, 63),
    (63, 105),
    (105, 66),
    (66, 107),
    # Face oval.
    (10, 338),
    (338, 297),
    (297, 332),
    (332, 284),
    (284, 251),
    (251, 389),
    (389, 356),
    (356, 454),
    (454, 323),
    (323, 361),
    (361, 288),
    (288, 397),
    (397, 365),
    (365, 379),
    (379, 378),
    (378, 400),
    (400, 377),
    (377, 152),
    (152, 148),
    (148, 176),
    (176, 149),
    (149, 150),
    (150, 136),
    (136, 172),
    (172, 58),
    (58, 132),
    (132, 93),
    (93, 234),
    (234, 127),
    (127, 162),
    (162, 21),
    (21, 54),
    (54, 103),
    (103, 67),
    (67, 109),
    (109, 10)
])

LIP_CONNECTIONS = frozenset([
    # Lips.
    (61, 146),  # v outer lower
    (146, 91),
    (91, 181),
    (181, 84),
    (84, 17),  # R
    (17, 314),  # L
    (314, 405),
    (405, 321),
    (321, 375),
    (375, 291),  # ^ outer lower
    (61, 185),  # v outer upper
    (185, 40),
    (40, 39),
    (39, 37),
    (37, 0),  # R
    (0, 267),  # L
    (267, 269),
    (269, 270),
    (270, 409),
    (409, 291),  # ^ outer upper
    (78, 95),  # v inner lower
    (95, 88),
    (88, 178),
    (178, 87),
    (87, 14),  # R
    (14, 317),  # L
    (317, 402),
    (402, 318),
    (318, 324),
    (324, 308),  # ^ inner lower
    (78, 191),  # v inner upper
    (191, 80),
    (80, 81),
    (81, 82),
    (82, 13),  # R
    (13, 312),  # L
    (312, 311),
    (311, 310),
    (310, 415),
    (415, 308)  # ^ inner upper
])

RIGHT_EYE_CONNECTIONS = frozenset([
    # Right eye.
    (33, 7),  # v lower, outside
    (7, 163),
    (163, 144),
    (144, 145),
    (145, 153),
    (153, 154),
    (154, 155),
    (155, 133),  # ^ lower, inside
    (33, 246),  # v upper, outside
    (246, 161),
    (161, 160),
    (160, 159),
    (159, 158),
    (158, 157),
    (157, 173),
    (173, 133)  # ^ upper, inside
])

LEFT_EYE_CONNECTIONS = frozenset([
    # Left eye.
    (263, 249),  # v lower, outside
    (249, 390),
    (390, 373),
    (373, 374),
    (374, 380),
    (380, 381),
    (381, 382),
    (382, 362),  # ^ lower, inside
    (263, 466),  # v upper, outside
    (466, 388),
    (388, 387),
    (387, 386),
    (386, 385),
    (385, 384),
    (384, 398),
    (398, 362)  # ^ upper, inside
])


def extract_points(points, connections):
    indices = list(set(list(itertools.chain.from_iterable(connections))))
    new_points = list(map(lambda x: points[x], indices))
    return new_points


def extract_lip_points(points):
    return extract_points(points, LIP_CONNECTIONS)


def extract_right_eye_points(points):
    return extract_points(points, RIGHT_EYE_CONNECTIONS)


def extract_left_eye_points(points):
    return extract_points(points, LEFT_EYE_CONNECTIONS)


def calc_eyes_params(face_points):
    # eye blink
    eyes_distance = np.linalg.norm(face_points[133] - face_points[362])  # for normalize
    r_eye_length = np.linalg.norm(face_points[33] - face_points[133]) / eyes_distance
    r_eye_distance = np.linalg.norm(face_points[145] - face_points[159]) / eyes_distance
    r_eye_area = r_eye_distance * r_eye_length
    r_eye_ndist = r_eye_distance / r_eye_length
    r_eye_blink = 1.0 - r_eye_ndist
    # r_eye_blink = 1.0 - (r_eye_distance / eyes_distance)

    l_eye_length = np.linalg.norm(face_points[263] - face_points[362]) / eyes_distance
    l_eye_distance = np.linalg.norm(face_points[374] - face_points[386]) / eyes_distance
    l_eye_area = l_eye_distance * l_eye_length
    l_eye_ndist = l_eye_distance / l_eye_length
    l_eye_blink = 1.0 - l_eye_ndist
    # l_eye_blink = 1.0 - (l_eye_distance / eyes_distance)

    return (
        r_eye_blink, r_eye_length, r_eye_distance, r_eye_area, r_eye_ndist,
        l_eye_blink, l_eye_length, l_eye_distance, l_eye_area, l_eye_ndist)


def calc_mouth_params(face_points):
    eyes_distance = np.linalg.norm(face_points[133] - face_points[362])  # for normalize

    # mouth shape
    lip_distance = np.linalg.norm(face_points[13] - face_points[14])
    lip_edges_center = 0.5 * (face_points[78] + face_points[308])
    lip_center_center = 0.5 * (face_points[13] + face_points[14])
    mouth_vector = face_points[0] - face_points[17]
    lip_edges_center_vector = lip_edges_center - face_points[17]
    lip_center_center_vector = lip_center_center - face_points[17]

    mouth_open = lip_distance / eyes_distance
    t_lip_edges_center = np.dot(mouth_vector, lip_edges_center_vector)
    t_lip_center_center = np.dot(mouth_vector, lip_center_center_vector)
    smile = (t_lip_edges_center - t_lip_center_center) / eyes_distance

    return (mouth_open, smile)


def calc_face_transform(face_points):
    r_eye_pt = 0.5 * (face_points[33] + face_points[133])
    l_eye_pt = 0.5 * (face_points[263] + face_points[362])
    lip_pt = 0.5 * (face_points[13] + face_points[14])

    x_vec = l_eye_pt - r_eye_pt
    y_vec = lip_pt - 0.5 * (r_eye_pt + l_eye_pt)
    x_vec /= np.linalg.norm(x_vec)
    y_vec /= np.linalg.norm(y_vec)
    z_vec = np.cross(x_vec, y_vec)

    face_co = np.eye(3)
    face_co[:3, 0] = x_vec
    face_co[:3, 1] = y_vec
    face_co[:3, 2] = z_vec
    face_pos = np.array([0.0, 0.0, 0.0])

    return (face_pos, face_co)
