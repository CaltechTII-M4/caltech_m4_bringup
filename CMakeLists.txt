cmake_minimum_required(VERSION 3.5)
project(caltech_m4_bringup CXX)

# Find dependencies
find_package(ament_cmake REQUIRED)

# Install the launch files
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}/
)

# Export package information
ament_package()
