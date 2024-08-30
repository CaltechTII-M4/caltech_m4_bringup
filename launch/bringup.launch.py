# #!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    EnvironmentVariable,
    PythonExpression,
)
from launch_ros.actions import Node
from swarm_launch_utils.utils import RewrittenYaml
from swarm_launch_utils.substitutions import IfElseSubstitution


def generate_launch_description():
    # Declare GLP
    glp_dir = get_package_share_directory("glp_ros")
    glp_params = os.path.join(
        glp_dir, "config", "precision_controller_params.yaml"
    )
    glp_param_file = LaunchConfiguration("glp_params_file", default=glp_params)

    behaviour_trees_directory = get_package_share_directory("caltech_m4_bringup")
    bt_param_file_default = os.path.join(
        behaviour_trees_directory, "params", "bt_params.yaml"
    )
    default_bt_path = LaunchConfiguration(
        "bt_path",
        default=os.path.join(
            behaviour_trees_directory,
            "behavior_trees_xml",
            "caltech.xml",
        ),
    )

    bt_params_file = LaunchConfiguration(
        "bt_params_file", default=bt_param_file_default
    )

    uav_name = EnvironmentVariable("UAV_NAME")
    uav_type = EnvironmentVariable("UAV_TYPE")
    run_type = EnvironmentVariable("RUN_TYPE")
    netbox_ip = EnvironmentVariable("NETBOX_IP")
    uav_id = EnvironmentVariable("UAV_ID")
    uav_name_param = LaunchConfiguration("uav_name", default=uav_name)
    uav_id_param = LaunchConfiguration("uav_id", default=uav_id)
    uav_type_param = LaunchConfiguration("uav_type", default=uav_type)

    sim = IfElseSubstitution(
        IfCondition(PythonExpression(["'", run_type, "' == ", "'simulation'"])),
        LaunchConfiguration("simulation", default="true"),
        LaunchConfiguration("simulation", default="false"),
    )

    lifecycle_nodes = [
        "swarm_bt_tasker",
        "glp_ros",
    ]

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    substitutions = {
        "uav_name": uav_name_param,
        "uav_type": uav_type_param,
        "uav_id": uav_id,
        "use_sim_time": use_sim_time,
        "simulation": sim,
        "netbox_ip": netbox_ip,
    }

    parsed_config_file_bt = RewrittenYaml(
        source_file=bt_params_file,
        param_rewrites={"default_bt": default_bt_path},
        root_key=uav_name_param,
        convert_types=True,
    )

    parsed_config_glp = RewrittenYaml(
        source_file=glp_param_file,
        param_rewrites={},
        root_key=uav_name_param,
        convert_types=True,
    )

    bt_node = Node(
        package="swarm_bt_server",
        executable="swarm_bt_tasker",
        name="swarm_bt_tasker",
        output="screen",
        parameters=[parsed_config_file_bt],
        namespace=uav_name_param,
    )

    mgr = Node(
        package="swarm_lifecycle_manager",
        executable="lifecycle_manager",
        name="mission_manager",
        output="screen",
        namespace=uav_name_param,
        parameters=[
            {"use_sim_time": use_sim_time},
            {"autostart": True},
            {"node_names": lifecycle_nodes},
        ],
    )

    glp = Node(
        package="glp_ros",
        executable="glp_ros",
        name="glp_ros",
        output="screen",
        parameters=[parsed_config_glp],
        namespace=uav_name_param,
    )

    ld = LaunchDescription()
    ld.add_action(mgr)
    ld.add_action(bt_node)
    ld.add_action(glp)

    return ld
