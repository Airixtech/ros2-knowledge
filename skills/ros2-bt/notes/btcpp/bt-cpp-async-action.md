---
id: bt-cpp-async-action
type: reference
owner: equipo-ros2
updated: 2026-10-15
review_by: 2027-04-13
source: manual
confidentiality: internal
title: "AsyncActionNode: RUNNING on a thread, halt()"
domain: bt
area: btcpp
distro: humble
tested: false
audience: dev
summary: "Asynchronous actions in BehaviorTree.CPP v3.8: course AnalyzeCPU and its halt bug, isHaltRequested, StatefulActionNode SleepNode, bt_u4_ex3."
tags: [AsyncActionNode, StatefulActionNode, ThreadedAction, halt, isHaltRequested, onStart, onRunning, onHalted, ReactiveSequence, bt_u4_ex3]
see: ["[[bt-reactive-async]]", "[[bt-concurrency]]", "[[bt-cpp-sync-action-ports]]", "[[bt-ros2-shared-node]]"]
requires: [ros2-core]
version_notes:
  - "all: the course halt() sets its own flag to false and never calls AsyncActionNode::halt(): the loop never stops — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/action_node.h (BT-V01)"
  - "all: StatefulActionNode is the preferred way to implement asynchronous actions; AsyncActionNode is hard to implement correctly — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/action_node.h (BT-V13)"
  - "v4: AsyncActionNode is ThreadedAction (alias kept) — https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/include/behaviortree_cpp/action_node.h (BT-V23)"
---
# AsyncActionNode: RUNNING on a thread, halt()

**TL;DR** To make an action asynchronous in v3.8 you inherit from `AsyncActionNode` (its `tick()` runs on a separate thread and the node returns RUNNING meanwhile) or, preferably, from `StatefulActionNode` (`onStart` / `onRunning` / `onHalted`, no thread). An `AsyncActionNode` must check `isHaltRequested()` in its loop and, if it overrides `halt()`, call `AsyncActionNode::halt()`. The course example does neither. [v4: `ThreadedAction`]

Because the `tick()` of an `AsyncActionNode` runs on its own thread, it may call blocking functions while the tree keeps running; that is exactly why it must stop when halted.

## Course code: `AnalyzeCPU` (do not copy the halt)
```cpp
class AnalyzeCPU: public AsyncActionNode
{
private:
  std::atomic_bool _halt_requested;
public:
  AnalyzeCPU(const std::string& name, const NodeConfiguration& config):
    AsyncActionNode(name,config)
  {}
  // you have to override
  virtual void halt() override;
  NodeStatus tick() override
  {
    auto res = getInput<CPU>("input");
    if( !res )
    {
      throw RuntimeError("error reading port [input]:", res.error() );
    }
    CPU usage = res.value();
    _halt_requested.store(false);
    int count = 0;
    while ((!_halt_requested) && (count < 10))
    {
      std:: cout << "analyzing for :: " << count << "\n";
      std::this_thread::sleep_for(std::chrono::seconds(1));
      count ++;
    }
    printf("Analyze CPU ::: [ %.1f ]\n", usage.cpu );
    //return NodeStatus::SUCCESS;
    std::cout << "[ Analysis process: FINISHED ]" << std::endl;
    return _halt_requested ? BT::NodeStatus::FAILURE : BT::NodeStatus::SUCCESS;
  }
  static PortsList providedPorts()
  {
    // Optionally, a port can have a human readable description
    const char*  description = "Simply print cpu usage on terminal...";
    return { InputPort<CPU>("input", description) };
  }
};
void AnalyzeCPU::halt()
{
  _halt_requested.store(false);
  std::cout << __FUNCTION__ << " called!" << "\n";
}
```
**Bug:** `halt()` stores `false`, so `_halt_requested` is never `true` and the loop always runs its 10 s; and the base `AsyncActionNode::halt()` (which sets the real halt flag and waits for the thread) is never called. BehaviorTree.CPP 3.8 asks for three things ([action_node.h](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/include/behaviortree_cpp_v3/action_node.h)): check `isHaltRequested()` periodically in `tick()`; in an overridden `halt()`, clean up and call `AsyncActionNode::halt()`; a halted action returns `NodeStatus::IDLE` (with few exceptions).

The fix, as a patch to the code above (not built here `[verify]`):
```cpp
    while (!isHaltRequested() && (count < 10))      // base-class flag, set by AsyncActionNode::halt()
    { /* … same body … */ }
    if (isHaltRequested())
    {
      return NodeStatus::IDLE;
    }
// …
void AnalyzeCPU::halt()
{
  std::cout << __FUNCTION__ << " called!" << "\n";
  AsyncActionNode::halt();                          // sets the flag and waits for the thread
}
```
Remove the private `_halt_requested` and its `store(false)` at the start of `tick()`.

## Preferred: StatefulActionNode (official 3.8 example)
```cpp
// Example of Asynchronous node that use StatefulActionNode as base class
class SleepNode : public BT::StatefulActionNode
{
  public:
    SleepNode(const std::string& name, const BT::NodeConfiguration& config)
      : BT::StatefulActionNode(name, config)
    {}

    static BT::PortsList providedPorts()
    {
      // amount of milliseconds that we want to sleep
      return{ BT::InputPort<int>("msec") };
    }

    NodeStatus onStart() override
    {
      int msec = 0;
      getInput("msec", msec);

      if( msec <= 0 ) {
        // No need to go into the RUNNING state
        return NodeStatus::SUCCESS;
      }
      else {
        using namespace std::chrono;
        // once the deadline is reached, we will return SUCCESS.
        deadline_ = system_clock::now() + milliseconds(msec);
        return NodeStatus::RUNNING;
      }
    }

    /// method invoked by an action in the RUNNING state.
    NodeStatus onRunning() override
    {
      if ( std::chrono::system_clock::now() >= deadline_ ) {
        return NodeStatus::SUCCESS;
      }
      else {
        return NodeStatus::RUNNING;
      }
    }

    void onHalted() override
    {
      // nothing to do here...
      std::cout << "SleepNode interrupted" << std::endl;
    }

  private:
    std::chrono::system_clock::time_point deadline_;
};
```
Source: [asynchronous_nodes.md (v3.8)](https://github.com/BehaviorTree/BehaviorTree.CPP/blob/v3.8/docs/asynchronous_nodes.md). No thread: each tick calls `onRunning()`, which must return quickly.

## The course run (`bt_u4_ex3`)
```text
[R→] ReactiveSequence name="root_sequence"
├── AnalyzeBattery name="battery_ok"
├── GetCPUusage      [OUT] usage = {CPUload}
└── AnalyzeCPU       [IN]  input = {CPUload}     asynchronous
```
Groot log of the first tick:
| Time | Node | Previous | Status |
|---|---|---|---|
| 0.000 | battery_ok | IDLE | SUCCESS |
| 0.000 | GetCPUusage | IDLE | SUCCESS |
| 0.000 | AnalyzeCPU | IDLE | RUNNING |
| 0.000 | root_sequence | IDLE | RUNNING |
```text
--- 1 executeTick() ---
Analyze Battery: battery_ok
current COUNTER ===> : 1
[ getting: FINISHED ]
analyzing for :: 0

--- 2 executeTick() ---
analyzing for :: Analyze Battery: battery_ok
current COUNTER ===> : 2
[ getting: FINISHED ]
1
analyzing for :: 2

--- 3 executeTick() ---
Analyze Battery: battery_ok
current COUNTER ===> : 3
[ getting: FINISHED ]
analyzing for :: 3

--- 4 executeTick() ---
Analyze Battery: battery_ok
current COUNTER ===> : 4
[ getting: FINISHED ]
analyzing for :: 4
analyzing for :: 5
analyzing for :: 6
analyzing for :: 7
analyzing for :: 8
analyzing for :: 9
Analyze CPU ::: [ 3.1 ]
[ Analysis process: FINISHED ]
```
The tree is ticked four times; the ReactiveSequence re-runs the battery check and the CPU reading on each tick, while `AnalyzeCPU` keeps counting on its own thread (the mixed line `analyzing for :: Analyze Battery: …` is two threads printing at once). The analysis finishes when the count reaches 10, independent of the ticks. The framework creates that thread for you.

## Pitfalls
- Every halt path matters: a ReactiveSequence halts the RUNNING child whenever an earlier child fails ([[bt-reactive-async]]).
- Two threads write to `std::cout`: interleaved lines are expected; protect shared data with atomics or mutexes.
