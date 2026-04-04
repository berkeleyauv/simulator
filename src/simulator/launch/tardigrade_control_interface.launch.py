# Copyright (c) 2026
# All rights reserved.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration as Lc
from launch.substitutions import PythonExpression
from launch_ros.actions import Node, PushRosNamespace

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    namespace = Lc('namespace')
    control_interface = Lc('control_interface')

    simulator_share = get_package_share_directory('simulator')

    thruster_manager_launch = os.path.join(
        get_package_share_directory('uuv_thruster_manager'),
        'launch',
        'thruster_manager.launch'
    )

    inertial_config = os.path.join(
        simulator_share,
        'config',
        'tardigrade',
        'inertial.yaml'
    )

    velocity_config = os.path.join(
        simulator_share,
        'config',
        'tardigrade',
        'vel_pid_control.yaml'
    )

    thruster_manager_config = os.path.join(
        simulator_share,
        'config',
        'tardigrade',
        'thruster_manager.yaml'
    )

    thruster_allocator = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(thruster_manager_launch),
        launch_arguments=[
            ('uuv_name', namespace),
            ('model_name', 'tardigrade'),
            ('config_file', thruster_manager_config),
            ('output_dir', os.path.join(simulator_share, 'config', 'tardigrade')),
            # Always recompute TAM from current spawned model to avoid stale matrix files.
            ('reset_tam', 'true'),
        ],
    )

    controller_group = GroupAction([
        PushRosNamespace(namespace),

        Node(
            package='uuv_control_cascaded_pid',
            executable='acceleration_control.py',
            name='acceleration_control',
            output='screen',
            parameters=[inertial_config],
        ),

        Node(
            condition=IfCondition(PythonExpression(["'", control_interface, "' == 'cmd_vel'"])),
            package='uuv_control_cascaded_pid',
            executable='velocity_control.py',
            name='velocity_control',
            output='screen',
            remappings=[
                ('odom', [ '/', namespace, '/pose_gt' ]),
            ],
            parameters=[velocity_config],
        ),
    ])

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='tardigrade'),
        DeclareLaunchArgument('control_interface', default_value='cmd_vel'),
        thruster_allocator,
        controller_group,
    ])
