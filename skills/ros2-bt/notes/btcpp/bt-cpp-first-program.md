---
id: bt-cpp-first-program
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "First BehaviorTree.CPP program: nodes, factory, XML, tickRoot (no ROS)"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Complete BehaviorTree.CPP v3 program bt_u2_ex1.cpp: SyncActionNode classes, simple conditions, factory, XML, tickRoot, build and output."
tags: [BehaviorTree.CPP, behaviortree_cpp_v3, SyncActionNode, registerNodeType, registerSimpleCondition, registerSimpleAction, createTreeFromText, tickRoot, cmake]
see: ["[[bt-cpp-registration]]", "[[bt-what-is-bt]]", "[[bt-cpp-factory]]", "[[bt-learn-unit2]]"]
requires: [ros2-core]
version_notes:
  - "v4: package behaviortree_cpp, headers behaviortree_cpp/…; Humble and Jazzy release both, Kilted/Lyrical only v4 — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (BT-V20)"
  - "v4: tickRoot() → tickOnce() / tickWhileRunning() — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/bt_factory.h (BT-V21)"
---
# First BehaviorTree.CPP program: nodes, factory, XML, tickRoot (no ROS)

**TL;DR** A BehaviorTree.CPP program has three parts: node classes (here `SyncActionNode`s that override `tick()`) or plain functions, the tree in XML, and a `main()` that registers every node ID in a `BehaviorTreeFactory`, creates the tree from the XML and ticks it. This is the course's first exercise (`bt_u2_ex1.cpp`, the pick-ball tree of [[bt-what-is-bt]]), with no ROS involved. [v4: `#include "behaviortree_cpp/bt_factory.h"`]

## bt_u2_ex1.cpp
```cpp
//"header" to BT - our software connection to BT framework
#include "behaviortree_cpp_v3/bt_factory.h"

using namespace BT;

/** Behavior Tree are used to create a logic to decide what
* to "do" and when.
* The exercises as it was discussed and depicted in the
* figure do not include a “connection” to ROS.
* The action for the robot, in our case, is defined as a separate C++ class.
*/

//C++ classes defines robot actions/behaviors
//----------------Class ApproachBall---------------------------------------
class ApproachBall : public BT::SyncActionNode // we inherit the SyncActionNode - for synchronous behaviour
//later we inherit the AsyncActionNode instead to run action in asynchronous mode. Details later
{
public:
  ApproachBall(const std::string& name) : BT::SyncActionNode(name, {})
  {
  }

  // You must override the virtual function tick()
  NodeStatus tick() override
  {
    //we just print on the terminal
    std::cout << "ApproachBall: " << this->name() << std::endl;
    //the action completes with SUCCESS, you can see below the action can "finish" with FAILURE
    return BT::NodeStatus::SUCCESS;
  }
};

//----------------Class FindBall------------------------------------------
class FindBall : public BT::SyncActionNode
{
public:
  FindBall(const std::string& name) : BT::SyncActionNode(name, {})
  {
  }

  // You must override the virtual function tick()
  NodeStatus tick() override
  {
    std::cout << "FindBall: " << this->name() << std::endl;
    return BT::NodeStatus::SUCCESS;
  }
};

//----------------Class PlaceBall------------------------------------------
class PlaceBall : public BT::SyncActionNode
{
public:
  PlaceBall(const std::string& name) : BT::SyncActionNode(name, {})
  {
  }

  // You must override the virtual function tick()
  NodeStatus tick() override
  {
    std::cout << "PlaceBall: " << this->name() << std::endl;
    return BT::NodeStatus::SUCCESS;
  }
};

//----------------Class GripperInterface------------------------------------------
class GripperInterface
{
private:
  bool _opened;

public:
  GripperInterface() : _opened(true)
  {
  }

  NodeStatus open()
  {
    _opened = true;
    std::cout << "GripperInterface::open" << std::endl;
    return BT::NodeStatus::SUCCESS;
  }

  NodeStatus close()
  {
    std::cout << "GripperInterface::close" << std::endl;
    _opened = false;
    return BT::NodeStatus::SUCCESS;
  }
};

BT::NodeStatus BallClose()
{
  std::cout << "[ Close to ball: NO ]" << std::endl;
  return BT::NodeStatus::FAILURE;
}

BT::NodeStatus BallGrasped()
{
  std::cout << "[ Grasped: NO ]" << std::endl;
  return BT::NodeStatus::FAILURE;
}

//definition of BT which reflects logical connection between robot actions
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------
static const char* xml_text = R"(
 <root main_tree_to_execute = "MainTree" >
     <BehaviorTree ID="MainTree">
        <Sequence name="root_sequence">
            <FindBall   name="ball_ok"/>
            <Sequence>
                <Fallback>
                    <BallClose   name="no_ball"/>
                    <ApproachBall    name="approach_ball"/>
                </Fallback>
                <Fallback>
                    <BallGrasped   name="no_grasp"/>
                    <GraspBall  name="grasp_ball"/>
                </Fallback>
            </Sequence>
            <PlaceBall   name="ball_placed"/>
        </Sequence>
     </BehaviorTree>
 </root>
 )";
//-------------------------------------------------------------------------
//-------------------------------------------------------------------------

int main()
{
  // We use the BehaviorTreeFactory to register our custom nodes
  BehaviorTreeFactory factory;

  //Node registration process
  factory.registerNodeType<ApproachBall>("ApproachBall");
  factory.registerNodeType<FindBall>("FindBall");
  factory.registerNodeType<PlaceBall>("PlaceBall");

  // Registering a SimpleActionNode using a function pointer.
  // you may also use C++11 lambdas instead of std::bind
  //this method is not recommended so we are not going to use any more
  factory.registerSimpleCondition("BallClose", std::bind(BallClose));
  factory.registerSimpleCondition("BallGrasped", std::bind(BallGrasped));

  //You can also create SimpleActionNodes using methods of a class
  //this method is not recommended so we are not going to use any more
  GripperInterface gripper;
  factory.registerSimpleAction("GraspBall", std::bind(&GripperInterface::close, &gripper));

  // Trees are created at deployment-time (i.e. at run-time, but only once at the beginning).
  // The currently supported format is XML.
  // IMPORTANT: when the object "tree" goes out of scope, all the TreeNodes are destroyed
  auto tree = factory.createTreeFromText(xml_text);

  // To "execute" a Tree you need to "tick" it.
  // The tick is propagated to the children based on the logic of the tree.
  tree.tickRoot();

  return 0;
}
```
`BallClose` and `BallGrasped` are registered as conditions, `GraspBall` as a simple action bound to a method of `GripperInterface`; the classes are registered with their XML ID. More on the registration methods: [[bt-cpp-registration]].

## Build and run
The course builds the BehaviorTree.CPP examples with plain CMake inside its course files:
```bash
cd ~/ros2_ws/src/bt_course_files/BehaviorTree.CPP
mkdir build && cd build
cmake ..
make
```
```bash
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/bt_course_files/BehaviorTree.CPP/build/course_bt
./bt_u2_ex1
```
```text
FindBall: ball_ok
[ Close to ball: NO ]
ApproachBall: approach_ball
[ Grasped: NO ]
GripperInterface::close
PlaceBall: ball_placed
```
- The root Sequence works as a logical AND: find, pick, place.
- `FindBall` succeeds (`ball_ok`); the ball is not close (`[ Close to ball: NO ]`, FAILURE), so the Fallback runs `ApproachBall`.
- The ball is not grasped (`[ Grasped: NO ]`), so the Fallback runs `GraspBall` (`GripperInterface::close`).
- The inner Sequence succeeds and `PlaceBall` runs.

## Pitfalls
- Every tag of the XML must be a registered ID (or a built-in node, [[bt-cpp-factory]]); an unknown tag makes `createTreeFromText` throw.
- The tree object owns the nodes: if `tree` goes out of scope, every TreeNode is destroyed.
- `tickRoot()` ticks once. That is enough here because every node is synchronous; with RUNNING nodes tick in a loop ([[bt-concurrency]]).
