from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration as Lc

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    singlefile_launch = os.path.join(
        get_package_share_directory('simulator'),
        'launch',
        'tardigrade_singlefile.launch.py'
    )

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='tardigrade'),
        DeclareLaunchArgument('x', default_value='15'),
        DeclareLaunchArgument('y', default_value='-15'),
        DeclareLaunchArgument('z', default_value='-3'),
        DeclareLaunchArgument('roll', default_value='0.0'),
        DeclareLaunchArgument('pitch', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('paused', default_value='false'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('verbose', default_value='true'),
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(singlefile_launch),
            launch_arguments=[
                ('namespace', Lc('namespace')),
                ('x', Lc('x')),
                ('y', Lc('y')),
                ('z', Lc('z')),
                ('roll', Lc('roll')),
                ('pitch', Lc('pitch')),
                ('yaw', Lc('yaw')),
                ('gui', Lc('gui')),
                ('paused', Lc('paused')),
                ('headless', Lc('headless')),
                ('verbose', Lc('verbose')),
                ('enable_control_interface', 'true'),
                ('control_interface', 'cmd_vel'),
            ],
        ),
    ])
