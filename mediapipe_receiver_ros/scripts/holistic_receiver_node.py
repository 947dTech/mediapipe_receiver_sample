#!/bin/sh
""":" .

if [ ${ROS_DISTRO} = "melodic" ] ; then
    exec python "$0" "$@"
else
    exec python3 "$0" "$@"
fi
"""

import sys
import socket
import time
import json
import numpy as np

import rospy
from std_msgs.msg import Header, ColorRGBA
from geometry_msgs.msg import Pose, Point, Vector3, Quaternion
from visualization_msgs.msg import Marker

## @param aspect_ratio aspect ration of smartphone display
##  2.17 = 19.5/9 for Google Pixel5
def landmarks_to_points(landmarks, aspect_ratio=2.17):
    points = []
    for lm in landmarks:
        point = np.asarray([lm["x"], lm["y"], lm["z"]], dtype=np.float64)
        points.append(point)
    return points

def create_marker_msg(stamp=rospy.Time(), r=1.0, g=0.0, b=0.0):
    marker = Marker()
    marker.header = Header(frame_id="smartphone/camera_frame", stamp=stamp)
    marker.ns = "mediapipe"
    marker.id = 0
    marker.pose = Pose(Point(0, 0, 0), Quaternion(0, 0, 0, 1))
    marker.type = Marker.LINE_LIST
    marker.action = Marker.DELETE  # NOTE: default DELETE
    marker.scale = Vector3(x=0.01, y=0.0, z=0.0)
    marker.color = ColorRGBA(r=r, g=g, b=b, a=1.0)
    marker.points = []
    return marker

def points_to_ros_points(points, indices, offset=np.array([0.0, 0.0, 0.0], dtype=np.float64)):
    ros_points = []
    for i, j in indices:
        p0 = points[i] + offset
        p1 = points[j] + offset
        ros_points.append(Point(x=p0[0], y=p0[1], z=p0[2]))
        ros_points.append(Point(x=p1[0], y=p1[1], z=p1[2]))
    return ros_points

def main():
    rospy.init_node("holistic_receiver_node", anonymous=True)

    pub_pose = rospy.Publisher("pose_landmarks", Marker)
    pub_face = rospy.Publisher("face_landmarks", Marker)
    pub_rhand = rospy.Publisher("right_hand_landmarks", Marker)
    pub_lhand = rospy.Publisher("left_hand_landmarks", Marker)

    host = ""  # empty for receiver
    port = 0x947d

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    pose_indices = [
        # right arm
        (11, 13),
        (13, 15),
        (15, 17),
        (15, 19),
        (17, 19),
        (15, 21),
        # left arm
        (12, 14),
        (14, 16),
        (16, 18),
        (16, 20),
        (18, 20),
        (16, 22),
        # right leg
        (23, 25),
        (25, 27),
        (27, 29),
        (27, 31),
        (29, 31),
        # left leg
        (24, 26),
        (26, 28),
        (28, 30),
        (28, 32),
        (30, 32),
        # face
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 7),
        (0, 4),
        (4, 5),
        (5, 6),
        (6, 8),
        (9, 10),
        # body
        (11, 12),
        (11, 23),
        (23, 24),
        (12, 24)
    ]

    hand_indices = [
        # thumb
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        # index
        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),
        # middle
        (0, 9),
        (9, 10),
        (10, 11),
        (11, 12),
        # ring
        (0, 13),
        (13, 14),
        (14, 15),
        (15, 16),
        # pinky
        (0, 17),
        (17, 18),
        (18, 19),
        (19, 20)
    ]

    # face connection is copied and modified from mediapipe/python/solutions/face_mesh.py
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
    face_indices = [
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
    ]

    try:
        while not rospy.is_shutdown():
            msg, sender = sock.recvfrom(65536)
            json_msg = msg.decode(encoding="utf-8")
            dict_msg = json.loads(json_msg)

            local_time = rospy.Time.now()

            has_pose = "pose_world_landmarks_stamp" in dict_msg
            has_face = "face_landmarks_stamp" in dict_msg
            has_rhand = "right_hand_landmarks_stamp" in dict_msg
            has_lhand = "left_hand_landmarks_stamp" in dict_msg

            if not has_pose:
                print("  no data.")
                continue

            pose_stamp = dict_msg["pose_world_landmarks_stamp"]
            pose_landmarks = dict_msg["pose_world_landmarks"]
            pose_points = landmarks_to_points(pose_landmarks, aspect_ratio=1.0)

            pose_marker = create_marker_msg(stamp=local_time, r=0.0, g=1.0, b=0.0)
            pose_marker.action = Marker.ADD
            pose_marker.points = points_to_ros_points(pose_points, pose_indices)

            face_stamp = 0.0
            face_stamp_delay = 0.0
            face_marker = create_marker_msg(stamp=local_time, r=1.0, g=1.0, b=0.0)
            update_face = False
            if has_face:
                face_stamp = dict_msg["face_landmarks_stamp"]
                face_stamp_delay = (face_stamp - pose_stamp)
                print("  face stamp : %f" % face_stamp)
                print("  face delay : %f" % face_stamp_delay)
                update_face = face_stamp_delay < 1e5  # mediapipe timestamp is in millisecond
            else:
                print("  face: no data")

            if update_face:
                face_marker.action = Marker.ADD
                face_landmarks = dict_msg["face_landmarks"]
                face_points = landmarks_to_points(face_landmarks)
                face_marker.points = points_to_ros_points(
                    face_points, face_indices, offset=(pose_points[0] - face_points[1]))

            rhand_stamp = 0.0
            rhand_stamp_delay = 0.0
            rhand_marker = create_marker_msg(stamp=local_time, r=1.0, g=0.0, b=0.0)
            update_rhand=False
            if has_rhand:
                rhand_stamp = dict_msg["right_hand_landmarks_stamp"]
                rhand_stamp_delay = (rhand_stamp - pose_stamp)
                print("  rhand stamp : %f" % rhand_stamp)
                print("  rhand delay : %f" % rhand_stamp_delay)
                update_rhand = rhand_stamp_delay < 1e5  # mediapipe timestamp is in millisecond
            else:
                print("  rhand: no data")

            if update_rhand:
                rhand_marker.action = Marker.ADD
                rhand_landmarks = dict_msg["right_hand_landmarks"]
                rhand_points = landmarks_to_points(rhand_landmarks)
                rhand_marker.points = points_to_ros_points(
                    rhand_points, hand_indices, offset=(pose_points[16] - rhand_points[0]))

            lhand_stamp = 0.0
            lhand_stamp_delay = 0.0
            lhand_marker = create_marker_msg(stamp=local_time, r=0.0, g=0.0, b=1.0)
            update_lhand=False
            if has_lhand:
                lhand_stamp = dict_msg["left_hand_landmarks_stamp"]
                lhand_stamp_delay = (lhand_stamp - pose_stamp)
                print("  lhand stamp : %f" % lhand_stamp)
                print("  lhand delay : %f" % lhand_stamp_delay)
                update_lhand = lhand_stamp_delay < 1e5  # mediapipe timestamp is in millisecond
            else:
                print("  lhand: no data")

            if update_lhand:
                lhand_marker.action = Marker.ADD
                lhand_landmarks = dict_msg["left_hand_landmarks"]
                lhand_points = landmarks_to_points(lhand_landmarks)
                lhand_marker.points = points_to_ros_points(
                    lhand_points, hand_indices, offset=(pose_points[15] - lhand_points[0]))

            pub_pose.publish(pose_marker)
            pub_face.publish(face_marker)
            pub_rhand.publish(rhand_marker)
            pub_lhand.publish(lhand_marker)
            
    except KeyboardInterrupt:
        sock.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
