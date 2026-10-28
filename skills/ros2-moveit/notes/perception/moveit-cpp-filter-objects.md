---
id: moveit-cpp-filter-objects
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "Several detected objects: print type and dimensions, keep the box that fits a size"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "Detected objects loop: primitives[0].type BOX=1, dimensions; keep the box under 0.05 x 0.05 x 0.10 m; print its pose."
tags: [filter objects, multiple objects, primitives, SolidPrimitive, type, BOX, dimensions, primitive_poses, get_object_pose_action_client, grasp_box2, object of interest, result_callback]
see: ["[[moveit-cpp-get-object-pose]]", "[[moveit-grasping-msgs]]", "[[moveit-scene-grasp-boxes]]", "[[moveit-learn-unit5]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: both course versions print objects[0]'s position for every object; the loop variable's pose is used below (MOVEIT-V09)"
  - "course: the text's bigger object (0.19 x 0.12 x 0.29) and the result shown do not match the 0.1 m second box [verify] (MOVEIT-V43)"
---
# Several objects: filter by type and size

**TL;DR** With a second object in the scene (the blue 0.1 m cube, [[moveit-scene-grasp-boxes]]), `objects[0]` may not be the box you want. Loop over all objects, read `object.primitives[0].type` and `.dimensions`, and keep the box (type 1) whose sides fit the target size; print **that object's** pose.

## Exercise 5.3: print every object (changes against [[moveit-cpp-get-object-pose]])
In `result_callback()`, after "Result: Received !", the single print of `objects[0]` becomes a loop (course comment "get all the objects from detected list of objects", header log "Result: Detected Object Positions:"):
```cpp
for (auto object : action_result.result->objects) {
  RCLCPP_INFO(this->get_logger(), "Type: %d", object.object.primitives[0].type);
  RCLCPP_INFO(this->get_logger(), "DimX: %+0.3f, DimY: %+0.3f, DimZ: %+0.3f", object.object.primitives[0].dimensions[0], object.object.primitives[0].dimensions[1], object.object.primitives[0].dimensions[2]);
  // MOVEIT-V09: the course prints action_result.result->objects[0]'s pose here, for every object
  RCLCPP_INFO(this->get_logger(), "PosX: %+0.3f, PosY: %+0.3f, PosZ: %+0.3f", object.object.primitive_poses[0].position.x, object.object.primitive_poses[0].position.y, object.object.primitive_poses[0].position.z);
}
```
- **Type**: the primitive shape, `BOX=1 SPHERE=2 CYLINDER=3 CONE=4` ([[moveit-grasping-msgs]]).
- **Dimensions**: the `[X, Y, Z]` sizes of the object.

## Exercise 5.4: keep only the box of interest
Known: the object is a box (type 1) and its URDF size is `<box size="0.04 0.04 0.08"/>`, so anything bigger can be discarded (the course's example run found one object of 0.19 × 0.12 × 0.29; MOVEIT-V43). Keep only a box within 0.05 × 0.05 × 0.10 m (course comment "get the desired object from detected list of objects / using type and dimensions to filter the object of interest", header log "Result: Filtered Object of Interest Position:"):
```cpp
for (auto object : action_result.result->objects) {
  if ((object.object.primitives[0].type == 1) &&
      (object.object.primitives[0].dimensions[0] < 0.050) &&
      (object.object.primitives[0].dimensions[1] < 0.050) &&
      (object.object.primitives[0].dimensions[2] < 0.100)) {
    RCLCPP_INFO(this->get_logger(), "Type: %d", object.object.primitives[0].type);
    RCLCPP_INFO(this->get_logger(), "DimX: %+0.3f, DimY: %+0.3f, DimZ: %+0.3f", object.object.primitives[0].dimensions[0], object.object.primitives[0].dimensions[1], object.object.primitives[0].dimensions[2]);
    // MOVEIT-V09: the course prints action_result.result->objects[0]'s pose here
    RCLCPP_INFO(this->get_logger(), "PosX: %+0.3f, PosY: %+0.3f, PosZ: %+0.3f", object.object.primitive_poses[0].position.x, object.object.primitive_poses[0].position.y, object.object.primitive_poses[0].position.z);
  } else {
    continue;
  }
}
```
The rest of the program is unchanged. Spawn the second box (`grasp_box2` at x 0.3, y 0.13) and run the client as in [[moveit-cpp-get-object-pose]].

## Pitfalls
- The course's two versions pair the current object's type and size with the **first** object's position: the filter then reports the wrong position whenever the box is not first (MOVEIT-V09).
- `primitives[0]` / `primitive_poses[0]` on an object without primitives is out of range: check the sizes ([[moveit-cpp-get-object-pose]]).
- `for (auto object : …)` copies every object (with its point cluster); `const auto & object` avoids it.
