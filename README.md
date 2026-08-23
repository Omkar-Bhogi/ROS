# ROS2-industrial-amr

Simulated mobile robot in ROS 2 + Gazebo that maps a small factory-style
environment using SLAM. Built to connect my robotics coursework with my actual
production/MES background, instead of just doing a generic "robot drives
around" tutorial project.

Everything here is simulation — no physical robot involved.

## What it does right now

- Simulated differential-drive robot (URDF/Xacro) with 2 wheels, a caster, and
  a 2D LiDAR
- Spawns in Gazebo Harmonic in a small factory world (4 walls + 2 station
  obstacles)
- Drives via `/cmd_vel`
- Runs SLAM (slam_toolbox) to build a 2D occupancy grid map from the LiDAR
  data as it drives around
- Map gets saved to disk (`.pgm` + `.yaml`)

Basically: drive it around manually, watch it build a map of the room in
RViz2, save the map.

## The annoying bug I had to fix

The LiDAR was publishing real data and slam_toolbox was running, but `/map`
just never produced anything — every scan was getting silently dropped.

Took a while to track down. Turned out the LiDAR's scan messages were
labeled with frame `amr/base_link/lidar`, but that frame didn't actually
exist anywhere in the TF tree — only `lidar_link` did. Two different parts
of the stack disagreed on what to call the same sensor:

- `robot_state_publisher` builds the TF tree from my original URDF, so it
  used `lidar_link` like I named it
- Gazebo internally merges/simplifies chains of fixed joints when it loads
  the robot (for performance), and in doing that it renamed the sensor
  frame internally to `amr/base_link/lidar`

So slam_toolbox got scan data pointing at a frame name that didn't exist,
and just threw it all away. Once I found this (mostly by walking the TF
tree with `tf2_echo`/`tf2_monitor` instead of guessing at slam_toolbox
params), the fix was adding a `static_transform_publisher` bridging the two
frame names — since they're literally the same physical point, a
zero-distance transform is correct, not a hack.

After that, `/map` started publishing real data and I could see a proper
map of the walls and both stations in RViz.

## Structure

src/
  task_manager/ - basic pub/sub practice,
  amr_description/
    urdf/amr.urdf.xacro 
    worlds/factory.sdf 
    launch/slam.launch.py 
    config/slam_params.yaml
maps/
  factory_map.pgm
  factory_map.yaml


## Running it

```bash
ros2 launch amr_description slam.launch.py
```

then in another terminal:

```bash
ros2 lifecycle set /slam_toolbox configure
ros2 lifecycle set /slam_toolbox activate

# drive it
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.3}}"

# stop it (cmd_vel keeps repeating until you overwrite it — Ctrl+C alone doesn't stop the robot)
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" -1
```

`rviz2` to watch the map build live. Save it with:

```bash
ros2 run nav2_map_server map_saver_cli -f maps/factory_map
```

Ubuntu 24.04 (WSL2), ROS 2 Jazzy, Gazebo Harmonic.

## Not done yet

- No autonomous navigation — right now I'm driving it manually with
  `cmd_vel`. Nav2 is next.
- Map coverage is from a short test drive, not the whole room.
- No connection to MQTT/OPC UA or a database yet — that's planned once
  navigation is working, similar to what I did in my
  [opcua-production-monitor](https://github.com/Omkar-Bhogi/opcua-production-monitor)
  project.

## Plan

1. ~~Basic ROS 2 pub/sub~~ ✅
2. ~~Simulated robot in Gazebo~~ ✅
3. ~~SLAM mapping~~ ✅
4. Nav2 autonomous navigation — next
5. Task manager (simulate the robot getting assigned "move part from A to B")
6. Bridge to MQTT/OPC UA
7. Log robot state to a database + Grafana dashboard
