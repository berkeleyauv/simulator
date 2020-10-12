import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():

    # launch paths
    simulator_dir = get_package_share_directory('simulator')

    world = LaunchConfiguration('world')

    declare_world_cmd = DeclareLaunchArgument(
        'world', default_value=os.path.join(simulator_dir, 'worlds', 'transdec.world'),
        description='Specify world file name'
    )

    # Create the launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')

    launch_gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory('gazebo_ros'), "/launch/gzserver.launch.py"]),
        launch_arguments={'world': world, 'verbose': 'true'}.items()
    )

    launch_gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([get_package_share_directory('gazebo_ros'), "/launch/gzclient.launch.py"])
    )

    set_use_sim_time_cmd = ExecuteProcess(
        cmd=['ros2', 'param', 'set', '/gazebo', 'use_sim_time', use_sim_time],
        output='screen')

    ld = LaunchDescription()
    ld.add_action(declare_world_cmd)
    ld.add_action(launch_gzserver_cmd)
    ld.add_action(launch_gzclient_cmd)
    ld.add_action(set_use_sim_time_cmd)
    return ld
