cmake_minimum_required(VERSION 3.5)
project(caltech_m4_bringup CXX)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(swarm_bt_server REQUIRED)
find_package(swarm_launch_utils REQUIRED)
find_package(swarm_lifecycle_manager REQUIRED)

# Install the launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

# Export package information
ament_package()
