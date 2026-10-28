---
id: moveit-simple-grasping-code
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "basic_grasping_perception.cpp walk-through: parameters, QoS, cloud callback, segmentation, action callbacks"
domain: moveit
area: perception
distro: humble
tested: false
audience: dev
summary: "basic_grasping_perception: debug_topics, frame_id, best-effort cloud subscription, cloud_callback (range filter, transformPointCloud, segment), handle_accepted thread, execute 3 s wait."
tags: [basic_grasping_perception.cpp, simple_grasping, cloud_callback, handle_goal, handle_cancel, handle_accepted, execute, ObjectSupportSegmentation, ShapeGraspPlanner, pcl_ros::transformPointCloud, PassThrough, range filter, pcl::fromROSMsg, toROSMsg, best_effort, debug_topics, frame_id, find_objects_, rclcpp_action::create_server]
see: ["[[moveit-simple-grasping]]", "[[moveit-find-objects-action]]", "[[moveit-grasping-msgs]]", "[[cpp-action-server]]", "[[core-qos-usage]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "humble: PCL >= 1.11 makes PointCloud::Ptr a std::shared_ptr, so the walk-through's boost::make_shared does not compile; the course's copy uses std::make_shared; the text names /wrist_camera/depth/points, the code subscribes /wrist_rgbd_depth_sensor/points — https://github.com/PointCloudLibrary/pcl/blob/master/CHANGES.md (MOVEIT-V07)"
  - "humble: execute() waits up to 3.0 s for a cloud; find_objects_ is a plain bool shared by two threads — https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/basic_grasping_perception.cpp (MOVEIT-V40)"
  - "humble: segmentation parameters of the release: cluster_tolerance 0.01, cluster_min_size 50, voxel_leaf_size 0.005, voxel_limit_min 0.0 (course copy -1.0), voxel_limit_max 1.8, voxel_field_name z; range filter z 0-2.5 m — https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/object_support_segmentation.cpp (MOVEIT-V37)"
---
# `basic_grasping_perception.cpp`: how the detection works

**TL;DR** The node ignores the camera clouds until a `find_objects` goal arrives. The goal handler starts a thread that sets `find_objects_ = true` and waits; the next cloud is range-filtered, transformed into `frame_id`, and split by `ObjectSupportSegmentation` into objects and support surfaces; the thread then fills the result. The fragments below are the course's walk-through of its copy (the released code differs only as listed in [[moveit-simple-grasping]]).

## Parameters and publishers
```cpp
debug_ = this->declare_parameter<bool>("debug_topics", false);
if (debug_) {
  rclcpp::QoS qos(1);
  qos.best_effort();
  object_cloud_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("object_cloud", qos);
  support_cloud_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("support_cloud", qos);
}
```
`debug_topics` true → two more topics with the points of the detected objects and of their surface (best effort: RViz2 needs Best Effort, [[moveit-find-objects-action]]).
```cpp
world_frame_ = this->declare_parameter<std::string>("frame_id", "base_link");
```
All detections are given in `base_link` (the "world frame" of the node).
```cpp
rclcpp::QoS points_qos(10);
points_qos.best_effort();
cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>("/wrist_rgbd_depth_sensor/points", points_qos, std::bind(&BasicGraspingPerception::cloud_callback, this, _1));
```
The depth camera's cloud. The course text says `/wrist_camera/depth/points`; the code subscribes `/wrist_rgbd_depth_sensor/points` (MOVEIT-V07).
```cpp
server_ = rclcpp_action::create_server<FindGraspableObjectsAction>(this->get_node_base_interface(), this->get_node_clock_interface(), this->get_node_logging_interface(), this->get_node_waitables_interface(), "find_objects", std::bind(&BasicGraspingPerception::handle_goal, this, _1, _2), std::bind(&BasicGraspingPerception::handle_cancel, this, _1), std::bind(&BasicGraspingPerception::handle_accepted, this, _1));
```
The `find_objects` action server that triggers the whole detection (action servers in C++: [[cpp-action-server]]).

## Cloud callback and goal callbacks
```cpp
void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
  // Be lazy
  if (!find_objects_)
    return;
  // Convert to point cloud
  // MOVEIT-V07: the course's walk-through shows boost::make_shared, which does not compile with PCL >= 1.11
  pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud = std::make_shared<pcl::PointCloud<pcl::PointXYZRGB>>();
  pcl::fromROSMsg(*msg, *cloud);
  RCLCPP_DEBUG(LOGGER, "Cloud recieved with %d points.", static_cast<int>(cloud->points.size()));
  // Filter out noisy long-range points
  pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud_filtered(new pcl::PointCloud<pcl::PointXYZRGB>);
  range_filter_.setInputCloud(cloud);
  range_filter_.filter(*cloud_filtered);
  RCLCPP_DEBUG(LOGGER, "Filtered for range, now %d points.", static_cast<int>(cloud_filtered->points.size()));
  // Transform to grounded
  pcl::PointCloud<pcl::PointXYZRGB>::Ptr cloud_transformed(new pcl::PointCloud<pcl::PointXYZRGB>);
  if (!pcl_ros::transformPointCloud(world_frame_, *cloud_filtered, *cloud_transformed, *buffer_)) {
    RCLCPP_ERROR(LOGGER, "Error transforming to frame %s", world_frame_.c_str());
    return;
  }
  // Run segmentation
  objects_.clear();
  supports_.clear();
  pcl::PointCloud<pcl::PointXYZRGB> object_cloud;
  pcl::PointCloud<pcl::PointXYZRGB> support_cloud;
  if (debug_) {
    object_cloud.header.frame_id = cloud_transformed->header.frame_id;
    support_cloud.header.frame_id = cloud_transformed->header.frame_id;
  }
  segmentation_->segment(cloud_transformed, objects_, supports_, object_cloud, support_cloud, debug_);
  if (debug_) {
    sensor_msgs::msg::PointCloud2 cloud_msg;
    pcl::toROSMsg(object_cloud, cloud_msg);
    object_cloud_pub_->publish(cloud_msg);
    pcl::toROSMsg(support_cloud, cloud_msg);
    support_cloud_pub_->publish(cloud_msg);
  }
  // Ok to continue processing
  find_objects_ = false;
}

rclcpp_action::GoalResponse handle_goal(const rclcpp_action::GoalUUID & uuid, std::shared_ptr<const FindGraspableObjectsAction::Goal> goal_handle) {
  return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse handle_cancel(const std::shared_ptr<FindGraspableObjectsGoal> goal_handle) {
  return rclcpp_action::CancelResponse::ACCEPT;
}
```
1. Convert the `PointCloud2` message to a PCL cloud for processing.
2. Filter out noisy, long-range points (`range_filter_`: a `PassThrough` on z, 0–2.5 m in the released code).
3. Transform the cloud into `frame_id`.
4. **Segmentation** (`object_support_segmentation.cpp`): separate the surface from the objects.
5. With `debug_topics`, publish both clouds; then clear the flag.

## Accepting a goal and filling the result
```cpp
void handle_accepted(const std::shared_ptr<FindGraspableObjectsGoal> goal_handle) {
  if (!planner_ || !segmentation_) {
    // Create planner
    planner_.reset(new ShapeGraspPlanner(this->shared_from_this()));
    // Create perception
    segmentation_.reset(new ObjectSupportSegmentation(this->shared_from_this()));
  }
  // Break off a thread
  std::thread{std::bind(&BasicGraspingPerception::execute, this, _1), goal_handle}.detach();
}
```
The first goal creates the segmentation object (and the grasp planner, unused with `plan_grasps: false`); every goal runs `execute()` in its own thread.
```cpp
void execute(const std::shared_ptr<FindGraspableObjectsGoal> goal_handle) {
  auto result = std::make_shared<FindGraspableObjectsAction::Result>();
  // Get objects
  find_objects_ = true;
  rclcpp::Time t = clock_->now();
  while (find_objects_ == true) {
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
    if (clock_->now() - t > rclcpp::Duration::from_seconds(3.0)) {
      find_objects_ = false;
      goal_handle->abort(result);
      RCLCPP_ERROR(LOGGER, "Failed to get camera data in allotted time.");
      return;
    }
  }
  const auto goal = goal_handle->get_goal();
  // Set object results
  for (size_t i = 0; i < objects_.size(); ++i) {
    grasping_msgs::msg::GraspableObject g;
    g.object = objects_[i];
    if (goal->plan_grasps) {
      // Plan grasps for object
      planner_->plan(objects_[i], g.grasps);
    }
    result->objects.push_back(g);
  }
  // Set support surfaces
  result->support_surfaces = supports_;
  goal_handle->succeed(result);
}
```
`execute()` sets `find_objects_` so the cloud callback works on the next cloud, polls every 20 ms for up to 3 s, then copies the objects (and grasps if asked) and the support surfaces into the result. The walk-through shows "allotted"; the course's repository copy logs "alloted", the release "allocated" (MOVEIT-V40).

## Members
```cpp
bool debug_;
std::shared_ptr<tf2_ros::Buffer> buffer_;
std::shared_ptr<tf2_ros::TransformListener> listener_;
std::string world_frame_;
bool find_objects_;
std::vector<grasping_msgs::msg::Object> objects_;
std::vector<grasping_msgs::msg::Object> supports_;
rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr object_cloud_pub_;
rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr support_cloud_pub_;
std::shared_ptr<ShapeGraspPlanner> planner_;
std::shared_ptr<ObjectSupportSegmentation> segmentation_;
rclcpp_action::Server<FindGraspableObjectsAction>::SharedPtr server_;
rclcpp::Clock::SharedPtr clock_;
pcl::PassThrough<pcl::PointXYZRGB> range_filter_;
```

## Pitfalls
- `find_objects_` is a plain `bool` written by the action thread and the cloud callback: a data race in C++ terms (`std::atomic<bool>` is the safe form, MOVEIT-V40).
- Segmentation parameters of the release (same node): `cluster_tolerance` 0.01, `cluster_min_size` 50, `voxel_leaf_size` 0.005, `voxel_limit_min` 0.0 (course copy −1.0), `voxel_limit_max` 1.8, `voxel_field_name` `z` (MOVEIT-V37).
