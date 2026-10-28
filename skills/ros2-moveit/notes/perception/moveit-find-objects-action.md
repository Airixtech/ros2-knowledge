---
id: moveit-find-objects-action
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Run the find_objects action: debug_topics, FindGraspableObjects goal and result, object and support clouds in RViz2"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "ros2 run simple_grasping basic_grasping_perception_node -p debug_topics:=true; send_goal /find_objects FindGraspableObjects plan_grasps false; object_cloud, support_cloud Best Effort."
tags: [find_objects, basic_grasping_perception_node, debug_topics, FindGraspableObjects, grasping_msgs/action/FindGraspableObjects, plan_grasps, ros2 action send_goal, object_cloud, support_cloud, Best Effort, RViz2, PointCloud2, perception.rviz, voxel_limit_min, remap]
see: ["[[moveit-simple-grasping]]", "[[moveit-grasping-msgs]]", "[[moveit-cpp-get-object-pose]]", "[[core-qos-usage]]", "[[core-action-cli-status]]"]
requires: [ros2-core]
version_notes:
  - "humble: debug publishers use rclcpp::QoS(1).best_effort(): RViz2 needs Best Effort — https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/basic_grasping_perception.cpp (MOVEIT-V38)"
  - "humble: the node publishes object_cloud and support_cloud; the package README calls the second surface_cloud — https://github.com/mikeferguson/simple_grasping/blob/jazzy/README.md (MOVEIT-V39)"
  - "humble: released package: --ros-args -p voxel_limit_min:=-1.0 -r /head_camera/depth_registered/points:=/wrist_rgbd_depth_sensor/points matches the course copy [verify] (MOVEIT-V37)"
  - "course: the result shown (a 9.57 x 4.96 x 0.008 m primitive at y -2.08, 2021 stamp) is from another scene [verify] (MOVEIT-V43)"
---
# Run the `find_objects` action

**TL;DR** Start `basic_grasping_perception_node` with `debug_topics:=true`, call the `/find_objects` action (`grasping_msgs/action/FindGraspableObjects`, `plan_grasps: false` for detection only), and read the objects and support surfaces from the result. Watch `/object_cloud` and `/support_cloud` in RViz2 with **Best Effort** reliability.

## Start the server
```bash
ros2 run simple_grasping basic_grasping_perception_node --ros-args -p debug_topics:=true
```
With the released package and the course's camera (MOVEIT-V37 [verify]):
```bash
ros2 run simple_grasping basic_grasping_perception_node --ros-args -p debug_topics:=true -p voxel_limit_min:=-1.0 -r /head_camera/depth_registered/points:=/wrist_rgbd_depth_sensor/points
```
Check (exercise 5.1):
```bash
ros2 action list
```
```
/find_objects
```
and `ros2 topic list` shows two more topics:
```
/object_cloud
/support_cloud
```
`/object_cloud` holds the points of the detected objects, `/support_cloud` the surface they stand on (published only with `debug_topics`).

## Call it (exercise 5.2)
```bash
ros2 action send_goal /find_objects grasping_msgs/action/FindGraspableObjects "{plan_grasps: false}"
```
`plan_grasps` chooses whether grasps are computed too. After some seconds:
```
Waiting for an action server to become available...
Sending goal:
     plan_grasps: false

Goal accepted with ID: 8700ae9645314b0d98018b446a2818f8

Result:
    objects:
- object:
    header:
      stamp:
        sec: 1634920618
        nanosec: 76980389
      frame_id: base_link
    name: ''
    support_surface: surface0
    properties: []
    point_cluster:
      header:
        stamp:
          sec: 0
          nanosec: 0
        frame_id: ''
      height: 1
      width: 1760
      fields:
      - name: x
        offset: 0
        datatype: 7
        count: 1
      - name: y
        offset: 4
        datatype: 7
        count: 1
      - name: z
        offset: 8
        datatype: 7
        count: 1
      - name: rgb
        offset: 16
        datatype: 7
        count: 1
      is_bigendian: false
      point_step: 32
      row_step: 56320
      data:
      - 103
      - 28
      - 208
      ...
      - 128
      - 63
      is_dense: true
    primitives:
    - type: 1
      dimensions:
      - 9.568283081054688
      - 4.955076992511749
      - 0.007858745753765106
    primitive_poses:
    - position:
        x: 0.48848390579223633
        y: -2.0752249658107758
        z: -0.09606975689530373
      orientation:
        x: 0.0
        y: 0.0
        z: 0.0
        w: 1.0
    meshes: []
    mesh_poses: []
    surface:
      coef:
      - -2.9003527743043378e-05
      - 2.6923982659354806e-05
      - 1.0
      - 0.10009085386991501

Goal finished with status: SUCCEEDED
```
The message is large; its fields are explained in [[moveit-grasping-msgs]]. This output does not match the course's scene (a 9.57 × 4.96 × 0.008 m box at y −2.08, with a 2021 stamp: it comes from another scene, MOVEIT-V43 [verify]); the course box is 0.04 × 0.04 × 0.08 m.

## See the detections in RViz2 (exercise 5.1.3)
`rviz2` with the robot model and the camera cloud (Fixed Frame e.g. `base_link`, the frame of the detections), two more `PointCloud2` displays on `/object_cloud` and `/support_cloud`, each with **Reliability Policy: Best Effort**: the node publishes them best effort, and a reliable subscriber receives nothing from a best-effort publisher (MOVEIT-V38, [[core-qos-usage]]). Send the goal again: the object and its surface appear. Save the configuration as `perception.rviz`.

## Pitfalls
- No cloud within 3 s after the goal → the action aborts ("Failed to get camera data in allotted time.", [[moveit-simple-grasping-code]]): wrong topic name or no camera.
- The package README calls the second topic `surface_cloud`; the code publishes `support_cloud` (MOVEIT-V39).
