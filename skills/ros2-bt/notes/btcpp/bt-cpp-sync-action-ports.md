---
id: bt-cpp-sync-action-ports
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "Custom SyncActionNode with ports: providedPorts, getInput, setOutput"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Custom SyncActionNode with NodeConfiguration constructor, tick() callback, OutputPort/InputPort in providedPorts, setOutput and getInput."
tags: [SyncActionNode, NodeConfiguration, providedPorts, OutputPort, InputPort, setOutput, getInput, tick callback, GetCPUusage, bt_u4_ex2]
see: ["[[bt-cpp-blackboard]]", "[[bt-cpp-async-action]]", "[[bt-cpp-registration]]", "[[bt-ros2-shared-node]]"]
requires: [ros2-core]
version_notes:
  - "v4: NodeConfiguration is NodeConfig (alias kept) — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/tree_node.h (BT-V24)"
  - "all: getInput<T>() returns Optional<T> (v3) / Expected<T> (v4), used the same way — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/tree_node.h (BT-V30)"
---
# Custom SyncActionNode with ports: providedPorts, getInput, setOutput

**TL;DR** The default way to create a node is to inherit from `SyncActionNode` (finishes in one tick) or, for long actions, from an asynchronous base ([[bt-cpp-async-action]]). A node with ports needs the constructor `(const std::string& name, const NodeConfiguration& config)` and a static `providedPorts()`. Inside `tick()`, `setOutput("port", value)` writes and `getInput<T>("port")` reads; the values travel through the blackboard ([[bt-cpp-blackboard]]). [v4: `NodeConfig`]

## A node that produces a value
`GetCPUusage` computes a value in its callback and sends it to another node through its output port `usage`:
```cpp
class GetCPUusage: public SyncActionNode, public ComputeUsage
{
private:
  float usage;
public:
  GetCPUusage(const std::string& name, const NodeConfiguration& config):
    SyncActionNode(name,config)
  {}
  //----------------------
  //node callback
  //----------------------
  NodeStatus tick() override
  {
    ComputeUsage cpu;
    auto cpu_load = cpu.calulateUsege(4,4.8);
    this->usage = cpu_load;
    CPU cpuX = {cpu_load};
    setOutput("usage", cpuX);
    return NodeStatus::SUCCESS;
  }
  static PortsList providedPorts()
  {
    return { OutputPort<CPU>("usage") };
  }
};
```
`ComputeUsage` (its method is spelled `calulateUsege` in the course code) and the struct `CPU` (with a field `cpu`) are course helpers whose definitions are not shown. Your own work goes inside the callback, for example a call to ROS 2:
```cpp
    //----------------------
    //node callback
    //----------------------
    NodeStatus tick() override
    {
      //here you can call e.g ROS
    }
```
(This skeleton must still return a `NodeStatus`.)

## Data flow between the two nodes
```text
Get CPU usage  (tick)
  callback(): ComputeUsage cpu;
              cpu_load = cpu.calculateUsage(4, 4.8) ┄┄▶ ComputeUsage::calculateUsage(int, float)
                                                ◀┄┄ return (int * float * 3.1415)
  output port: usage = {CPUload} ┄┄▶ blackboard entry CPUload
                                         ┆
Analyze CPU  (tick)                      ▼
  input port: usage = {CPUload} ┄┄▶ prints "Analyze CPU ::: 60.3"
```
4 · 4.8 · 3.1415 = 60.3. In the asynchronous version of the next note the reading node's port is called `input`.
```text
[ Battery: OK ]
ApproachObject: approach_object
GripperInterface::open
Analyze CPU ::: [ 60.3 ]
```
`bt_u4_ex2`: the tree of [[bt-cpp-registration]] plus the two nodes that exchange the CPU value through the port mechanism.

## Reading an input safely
```cpp
auto res = getInput<CPU>("input");
if( !res )
{
  throw RuntimeError("error reading port [input]:", res.error() );
}
CPU usage = res.value();
```

## Pitfalls
- Without `providedPorts()` (or with a different port name) `getInput`/`setOutput` fail: the name in the code, in `providedPorts()` and in the XML attribute must match.
- A custom type (here `CPU`) can be passed between nodes directly; to set it from an XML string you need a `convertFromString` specialization ([[bt-cpp-blackboard]]).
