# -*- coding:utf-8 -*-

import json

import math
import numpy as np

import itertools

# from mediapipe/python/solutions/face_mesh.py
# https://github.com/google/mediapipe/blob/v0.8.6/mediapipe/python/solutions/face_mesh.py
# this source code is redistributed under the Apache 2.0 License;
#
# Copyright 2020 The MediaPipe Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
