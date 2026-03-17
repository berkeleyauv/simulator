from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import GroupAction
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration as Lc
from launch_ros.actions import Node, PushRosNamespace

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    namespace = Lc('namespace')
    use_sim_time = Lc('use_sim_time')
    use_keyboard_teleop = Lc('use_keyboard_teleop')
    use_joystick_teleop = Lc('use_joystick_teleop')

    simulator_share = get_package_share_directory('simulator')
    thruster_manager_share = get_package_share_directory('uuv_thruster_manager')
    cascaded_pid_share = get_package_share_directory('uuv_control_cascaded_pid')
    teleop_share = get_package_share_directory('uuv_teleop')

    inertial_file = os.path.join(
        cascaded_pid_share,
        'config',
        'tardigrade',
        'inertial.yaml')

    vel_pid_file = os.path.join(
        cascaded_pid_share,
        'config',
        'tardigrade',
        'vel_pid_control.yaml')

    world_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(simulator_share, 'launch', 'robosub.launch')),
        launch_arguments=[
            ('gui', Lc('gui')),
            ('paused', Lc('paused')),
            ('use_sim_time', use_sim_time),
            ('set_timeout', Lc('set_timeout')),
            ('timeout', Lc('timeout')),
        ])

    spawn_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(simulator_share, 'launch', 'spawn_tardigrade.launch.py')),
        launch_arguments=[
            ('debug', Lc('debug')),
            ('namespace', namespace),
            ('x', Lc('x')),
            ('y', Lc('y')),
            ('z', Lc('z')),
            ('roll', Lc('roll')),
            ('pitch', Lc('pitch')),
            ('yaw', Lc('yaw')),
            ('use_ned_frame', Lc('use_ned_frame')),
        ])

    thruster_manager_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(thruster_manager_share, 'launch', 'thruster_manager.launch')),
        launch_arguments=[
            ('model_name', 'tardigrade'),
            ('uuv_name', namespace),
            ('reset_tam', Lc('reset_tam')),
        ])

    control_group = GroupAction([
        PushRosNamespace(namespace),
        Node(
            package='uuv_control_cascaded_pid',
            executable='acceleration_control.py',
            name='acceleration_control',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, inertial_file],
        ),
        Node(
            package='uuv_control_cascaded_pid',
            executable='velocity_control.py',
            name='velocity_control',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, vel_pid_file],
            remappings=[
                ('odom', ['/', namespace, '/pose_gt']),
                ('cmd_accel', ['/', namespace, '/cmd_accel']),
            ],
        ),
    ])

    keyboard_teleop_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(teleop_share, 'launch', 'uuv_keyboard_teleop.launch')),
        launch_arguments=[
            ('uuv_name', namespace),
            ('output_topic', 'cmd_vel'),
            ('message_type', 'twist'),
        ],
        condition=IfCondition(use_keyboard_teleop))

    joystick_teleop_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(teleop_share, 'launch', 'uuv_teleop.launch')),
        launch_arguments=[
            ('uuv_name', namespace),
            ('joy_id', Lc('joy_id')),
            ('output_topic', 'cmd_vel'),
            ('message_type', 'twist'),
            ('axis_yaw', Lc('axis_yaw')),
            ('axis_x', Lc('axis_x')),
            ('axis_y', Lc('axis_y')),
            ('axis_z', Lc('axis_z')),
        ],
        condition=IfCondition(use_joystick_teleop))

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='tardigrade'),
        DeclareLaunchArgument('debug', default_value='0'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('use_ned_frame', default_value='false'),

        DeclareLaunchArgument('x', default_value='15'),
        DeclareLaunchArgument('y', default_value='-15'),
        DeclareLaunchArgument('z', default_value='-3'),
        DeclareLaunchArgument('roll', default_value='0.0'),
        DeclareLaunchArgument('pitch', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),

        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('paused', default_value='false'),
        DeclareLaunchArgument('set_timeout', default_value='false'),
        DeclareLaunchArgument('timeout', default_value='0.0'),

        DeclareLaunchArgument('reset_tam', default_value='true'),

        DeclareLaunchArgument('use_keyboard_teleop', default_value='true'),
        DeclareLaunchArgument('use_joystick_teleop', default_value='false'),
        DeclareLaunchArgument('joy_id', default_value='0'),
        DeclareLaunchArgument('axis_yaw', default_value='0'),
        DeclareLaunchArgument('axis_x', default_value='4'),
        DeclareLaunchArgument('axis_y', default_value='3'),
        DeclareLaunchArgument('axis_z', default_value='1'),

        world_launch,
        spawn_launch,
        thruster_manager_launch,
        control_group,
        keyboard_teleop_launch,
        joystick_teleop_launch,
    ])
