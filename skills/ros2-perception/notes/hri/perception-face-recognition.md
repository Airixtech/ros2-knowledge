---
id: perception-face-recognition
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Face recognition node: reference encodings per person folder, compare_faces on Haar face crops, labels"
domain: perception
area: hri
distro: humble
tested: false
audience: dev
summary: "face_recognition library: reference database of 128-d encodings per person folder, Haar face crops, compare_faces tolerance 0.6, labeled image."
tags: [face recognition, face_recognition, face_encodings, compare_faces, load_image_file, known_face_locations, dlib, reference database, Haar cascade, cv2.putText, face_recognition.py, hri]
see: ["[[perception-face-eye-detection]]", "[[perception-haar-cascades]]", "[[perception-python-deps]]"]
requires: [ros2-core]
version_notes:
  - "face_recognition 1.4.0 (master): face_encodings(face_image, known_face_locations=None, num_jitters=1, model='small'); without locations it runs its own face detector; compare_faces(..., tolerance=0.6); load_image_file(mode='RGB'); boxes in (top, right, bottom, left) — https://github.com/ageitgey/face_recognition/blob/master/face_recognition/api.py (PERC-V26) [verify: tight crops]"
  - "course: `break` left only the inner loop, so one face could get several names; a flag now stops the person loop too (PERC-V25)"
  - "face_recognition needs dlib (README); rosdep: python3-dlib-pip, no key for face_recognition — https://github.com/ros/rosdistro/blob/master/rosdep/python.yaml (PERC-V27)"
---
# Face recognition node

**TL;DR** Build a reference database once (one folder of photos per person → their 128-dimension face encodings), then for each Haar face in the camera image compute its encoding and compare it with the database; draw the name of the first person that matches. `face_recognition` (built on dlib) expects **RGB** images.

## Goal and database
Face recognition goes beyond detection: it compares a detected face with known faces stored in a database or a set of reference faces. Course goal: tell the Mona Lisa from the woman sitting on the bench. Library: [face_recognition](https://face-recognition.readthedocs.io/en/latest/face_recognition.html) with OpenCV (install: [[perception-python-deps]]).

Database: about a dozen images of each face (the course gives them; screenshots of RViz's `Image` display work too) in two folders of the package's `data` folder, installed with `data_files`:
- `data/person1`: the woman on the bench
- `data/mona_lisa`: the Mona Lisa

## `face_recognition.py`
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import face_recognition
import os
from ament_index_python.packages import get_package_share_directory
from typing import Dict, List, Any


class FaceRecognitionNode(Node):

    def __init__(self) -> None:
        super().__init__('face_recognition_node')
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)
        self.face_publisher = self.create_publisher(Image, '/detected_faces/faces', 10)
        self.bridge = CvBridge()
        data_folder = os.path.join(get_package_share_directory('hri'), 'data')
        face_cascade_path = os.path.join(data_folder, 'haarcascade_frontalface_default.xml')
        if not os.path.isfile(face_cascade_path):
            self.get_logger().error("Cascade xml file not found")
            return
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        # Load reference database
        self.reference_database = self.load_reference_database()

    def load_reference_database(self) -> Dict[str, List[Any]]:
        """ Populate a database with facial encodings from a predefined set of reference images """
        reference_database = {}
        reference_images_directories = [os.path.join(get_package_share_directory('hri'), 'data', 'person1'), os.path.join(get_package_share_directory('hri'), 'data', 'mona_lisa')]

        for directory in reference_images_directories:
            # Retrieving person name by accessing last component of the 'directory' path
            person_name = os.path.basename(directory)
            reference_database[person_name] = []
            # Iterate over each file in specified directory
            for filename in os.listdir(directory):
                # searches for images files
                if filename.endswith('.png') or filename.endswith('.jpg'):
                    image_path = os.path.join(directory, filename)
                    # load image file and convert it into an image format compatible with the library
                    reference_image = face_recognition.load_image_file(image_path)
                    # compute the face encodings
                    reference_encoding = face_recognition.face_encodings(reference_image)
                    # checks if at least one face is detected in the image
                    if len(reference_encoding) > 0:
                        reference_database[person_name].append(reference_encoding[0])
                        self.get_logger().info(f"Face encoding found in {filename}! Let's add it to reference database for {person_name}")
                    else:
                        self.get_logger().warning(f"No face detected in {os.path.basename(directory)}/{filename}. Skipping...")
        self.get_logger().info(f"Finished loading the reference database")
        return reference_database

    def image_callback(self, msg: Image) -> None:
        """ Processes Image data to perform face detection and recognition """
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        # Converts the BGR image to grayscale, as face detection usually requires grayscale images
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        # Face detection using preloaded Haar Cascade classifier
        faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)

        # Check if any faces were detected
        if len(faces) > 0:
            # Process each detected face
            for (x, y, w, h) in faces:
                # Extract face ROI
                face_image = cv_image[y:y+h, x:x+w]
                # Convert to RGB (face_recognition uses RGB format)
                rgb_face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                # Generate a face encoding for the extracted face region
                face_encodings = face_recognition.face_encodings(rgb_face_image)
                # Check if at least one face encoding was generated
                if len(face_encodings) > 0:
                    matched = False  # PERC-V25: stop at the first person that matches
                    # Compare with reference encodings
                    for person_name, reference_encodings in self.reference_database.items():
                        for reference_encoding in reference_encodings:
                            # Compare the detected face encoding with each reference encoding
                            match = face_recognition.compare_faces([reference_encoding], face_encodings[0])
                            if match[0]:
                                # If match found, draw rectangle around detected face
                                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                                # Draw label with person's name
                                cv2.putText(cv_image, person_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                                self.get_logger().info(f"Recognized {person_name}!")
                                matched = True
                                break
                        if matched:
                            break
                else:
                    self.get_logger().warning("No face encoding detected.")
        else:
            self.get_logger().error("No faces detected yet ...")

        self.face_publisher.publish(self.bridge.cv2_to_imgmsg(cv_image, 'bgr8'))


def main(args=None) -> None:
    rclpy.init(args=args)
    face_recognition_node = FaceRecognitionNode()
    rclpy.spin(face_recognition_node)
    face_recognition_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- `__init__`: camera subscription, publisher of the labeled image on `/detected_faces/faces`, the Haar face cascade, and `load_reference_database()`.
- `load_reference_database()`: a dict mapping each person's name (the folder name, `os.path.basename`) to a list of encodings. Every `.png`/`.jpg` is loaded as a NumPy array (`load_image_file`), `face_encodings()` returns one encoding per face found, and the first is stored; images without a face are skipped with a warning.
- `image_callback()`: Haar detection on the gray image (`scaleFactor` 1.3, `minNeighbors` 5); each face box is cut from the BGR image, converted to RGB, and encoded. Each reference encoding is compared with `compare_faces()`; on a match the face gets a rectangle and the person's name. The course's `break` left only the inner loop, so the next person was still tried (PERC-V25). The annotated image is published every frame.

## Launch and test
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run hri face_recognition
```
Drive around with teleop and show `/detected_faces/faces` in RViz: the woman on the bench is labeled `person1`, and the Mona Lisa `mona_lisa`.

## Pitfalls
- "No face encoding detected." on clear faces → `face_encodings(rgb_face_image)` runs its own face detector again on the tight crop. Pass the crop as the face box, in (top, right, bottom, left) order: `face_recognition.face_encodings(rgb_face_image, known_face_locations=[(0, w, h, 0)])` (PERC-V26) `[verify]`.
- `compare_faces` uses `tolerance=0.6` by default ("lower is more strict"); with many people, pick the smallest `face_recognition.face_distance()` instead of the first match.
- `face_recognition` needs dlib with its Python bindings first; its README installs dlib from source and requires CMake (PERC-V27, [[perception-python-deps]]).
- Faces are personal data: check the privacy rules of the place where the robot records (consent, storage of the reference photos).
