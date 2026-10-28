---
id: moveit-grasping-msgs
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "grasping_msgs: FindGraspableObjects, GraspableObject, Object, primitive_poses and SolidPrimitive"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "FindGraspableObjects result: objects (GraspableObject) and support_surfaces; Object.primitives (SolidPrimitive type, dimensions) and primitive_poses (geometry_msgs/Pose)."
tags: [grasping_msgs, FindGraspableObjects, GraspableObject, Object, ObjectProperty, primitive_poses, primitives, shape_msgs/SolidPrimitive, BOX, SPHERE, CYLINDER, CONE, PRISM, dimensions, geometry_msgs/Pose, point_cluster, support_surfaces, moveit_msgs/Grasp, ros2 interface show]
see: ["[[moveit-find-objects-action]]", "[[moveit-cpp-get-object-pose]]", "[[moveit-cpp-filter-objects]]", "[[core-iface-std-types]]"]
requires: [ros2-core]
version_notes:
  - "humble: the definitions match grasping_msgs (ros2 branch); a few comments of the current Object.msg are worded differently — https://github.com/mikeferguson/grasping_msgs/tree/ros2 (MOVEIT-V41)"
  - "humble: shape_msgs/SolidPrimitive also has PRISM=5 and a polygon field; the course output lacks them (older distro) — https://github.com/ros2/common_interfaces/blob/humble/shape_msgs/msg/SolidPrimitive.msg (MOVEIT-V42)"
---
# grasping_msgs: where the object's pose is

**TL;DR** The `find_objects` result has two arrays: `objects` (`GraspableObject[]`) and `support_surfaces` (`Object[]`). Each `GraspableObject` holds an `Object` plus grasps. For manipulation read `object.primitives[i]` (shape type and dimensions) and `object.primitive_poses[i]` (its `geometry_msgs/Pose`).

## The action
```bash
ros2 interface show grasping_msgs/action/FindGraspableObjects
```
```
###########################################################
# This action is called for integrated object detection and
#  grasp planning, such as in base_grasping_perception

# Set to false to disable grasp planning, returning only the objects found
bool plan_grasps
---
# Graspable objects found
GraspableObject[] objects

# Additional, non-graspable objects which may be support surfaces
Object[] support_surfaces
---
# Publish objects as they are detected and grasp planned
GraspableObject object
```

## GraspableObject and Object
```bash
ros2 interface show grasping_msgs/msg/GraspableObject
```
```
###########################################################
# This message describes an object + grasp data
Object object
moveit_msgs/Grasp[] grasps
```
The grasps stay empty with `plan_grasps: false`; the object data is an `Object`:
```bash
ros2 interface show grasping_msgs/msg/Object
```
```
###########################################################
# This message describes an object.

# Many of the geometric items below lack a stamp/frame_id,
# header stamp/frame_id should be used there
std_msgs/Header header

# An object might have a name
string name

# An object might have a known (named) support surface
string support_surface

# Objects might have properties, such as type/class, color, etc.
ObjectProperty[] properties

###########################################################
# Objects have many possible descriptions
#  The following are the possible description formats

# Perception modules often represent an object as a cluster of points
#  Is considered valid if the number of points > 0
sensor_msgs/PointCloud2 point_cluster

# MoveIt prefers solid primitives or meshes as a description of objects
shape_msgs/SolidPrimitive[] primitives
geometry_msgs/Pose[] primitive_poses

shape_msgs/Mesh[] meshes
geometry_msgs/Pose[] mesh_poses

# An object representing a support surface might be described by a plane
# Is considered valid if coefficients are not all 0s.
shape_msgs/Plane surface
```
The poses of the primitives are what you need:
```
geometry_msgs/Pose[] primitive_poses
```
A **primitive** is a basic solid shape (box, cylinder, cone, sphere; planes describe surfaces); MoveIt prefers primitives or meshes as object descriptions. Each pose is a `geometry_msgs/Pose`:
```bash
ros2 interface show geometry_msgs/msg/Pose
```
```
# A representation of pose in free space, composed of position and orientation.
Point position
Quaternion orientation
```
in the frame of `object.header` (`base_link` by default, [[moveit-find-objects-action]]).

## SolidPrimitive: type and dimensions
The shape and size of each primitive are in `primitives` (`shape_msgs/SolidPrimitive[] primitives`):
```bash
ros2 interface show shape_msgs/msg/SolidPrimitive
```
```
# Defines box, sphere, cylinder, and cone.
# All shapes are defined to have their bounding boxes centered around 0,0,0.
uint8 BOX=1
uint8 SPHERE=2
uint8 CYLINDER=3
uint8 CONE=4
# The type of the shape
uint8 type
# The dimensions of the shape
float64[<=3] dimensions  # At no point will dimensions have a length > 3.
# The meaning of the shape dimensions: each constant defines the index in the 'dimensions' array.
# For type BOX, the X, Y, and Z dimensions are the length of the corresponding sides of the box.
uint8 BOX_X=0
uint8 BOX_Y=1
uint8 BOX_Z=2
# For the SPHERE type, only one component is used, giving the sphere's radius.
uint8 SPHERE_RADIUS=0
# The center line is oriented along the Z-axis for the CYLINDER and CONE types, 
# Therefore, the CYLINDER_HEIGHT (CONE_HEIGHT) component of dimensions gives the
# height of the cylinder (cone).
# The CYLINDER_RADIUS (CONE_RADIUS) component of dimensions provides the radius of
# the base of the cylinder (cone).
# Cone and cylinder primitives are defined to be circular. Therefore, the tip of the cone
# is pointing up along the +Z axis.
uint8 CYLINDER_HEIGHT=0
uint8 CYLINDER_RADIUS=1
uint8 CONE_HEIGHT=0
uint8 CONE_RADIUS=1
```
So `type` 1 is a box (`BOX=1 SPHERE=2 CYLINDER=3 CONE=4`) and `dimensions` holds its X, Y, Z sizes. Humble's `SolidPrimitive` also defines `PRISM=5` with a `polygon` field; the course's output comes from an older distro (MOVEIT-V42).

## Pitfalls
- `objects`, `primitives` and `primitive_poses` can be empty: check sizes before indexing ([[moveit-cpp-get-object-pose]]).
- A supporting table comes back in `support_surfaces`, not in `objects`; the plane coefficients are in `surface.coef`.
