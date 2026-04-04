# Copyright (c) 2020 The Plankton Authors.
# All rights reserved.
#
# This source code is derived from UUV Simulator
# (https://github.com/uuvsimulator/uuv_simulator)
# Copyright (c) 2016-2019 The UUV Simulator Authors
# licensed under the Apache license, Version 2.0
# cf. 3rd-party-licenses.txt file in the root directory of this source tree.
#
from launch import LaunchDescription
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
from launch.actions import DeclareLaunchArgument
from launch.actions import GroupAction
from launch.actions import OpaqueFunction
from launch.actions import IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration as Lc

import launch_testing.actions

from ament_index_python.packages import get_package_share_directory

import os
import pathlib
import xacro


def to_bool(value: str):
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise ValueError('String to bool, invalid type ' + str(value))

    valid = {'true':True, '1':True,
             'false':False, '0':False}
    
    if value.lower() in valid:
        return valid[value]
    
    raise ValueError('String to bool, invalid value: %s' % value)


# =============================================================================
def launch_setup(context, *args, **kwargs): 
    # Perform substitutions
    debug = Lc('debug').perform(context)
    namespace = Lc('namespace').perform(context)
    use_sim_time = to_bool(Lc('use_sim_time').perform(context))
    gui = to_bool(Lc('gui').perform(context))
    paused = to_bool(Lc('paused').perform(context))
    headless = to_bool(Lc('headless').perform(context))
    verbose = to_bool(Lc('verbose').perform(context))
    x = Lc('x').perform(context)
    y = Lc('y').perform(context)
    z = Lc('z').perform(context)
    roll = Lc('roll').perform(context)
    pitch = Lc('pitch').perform(context)
    yaw = Lc('yaw').perform(context)
    use_world_ned = Lc('use_ned_frame').perform(context)
    enable_control_interface = to_bool(Lc('enable_control_interface').perform(context))
    control_interface = Lc('control_interface').perform(context)

    global_sim_time = Node(
        name='plankton_global_sim_time',
        package='plankton_utils',
        executable='plankton_global_sim_time',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    gazebo_launch = os.path.join(
        get_package_share_directory('gazebo_ros'),
        'launch',
        'gazebo.launch.py'
    )

    world_file = os.path.join(
        get_package_share_directory('simulator'),
        'worlds',
        'transdec.world'
    )

    gazebo_args = [
        ('world', world_file),
        ('pause', str(paused).lower()),
        ('use_sim_time', str(use_sim_time).lower()),
        ('gui', str(gui).lower()),
        ('headless', str(headless).lower()),
        ('debug', 'false'),
        ('verbose', str(verbose).lower()),
        ('extra_gazebo_args', '-s libgazebo_ros_force_system.so --ros-args -r gazebo:__ns:=/gazebo'),
    ]

    gazebo_world = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(gazebo_launch),
        launch_arguments=gazebo_args,
    )

    control_launch_file = os.path.join(
        get_package_share_directory('simulator'),
        'launch',
        'tardigrade_control_interface.launch.py'
    )

    if not pathlib.Path(control_launch_file).exists():
        exc = 'Launch file ' + control_launch_file + ' does not exist'
        raise Exception(exc)

    control_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(control_launch_file),
        launch_arguments=[
            ('namespace', namespace),
            ('control_interface', control_interface),
        ],
    )

    # Xacro
    xacro_file = os.path.join(
        get_package_share_directory('simulator'),
        'robots',
        'tardigrade_default.xacro'
    )

    # Build the directories, check for existence
    path = os.path.join(
        get_package_share_directory('simulator'),
        'robots',
        'generated',
        namespace,
    )

    if not pathlib.Path(path).exists():
        try:
            # Create directory if required and sub-directory
            os.makedirs(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
    
    output = os.path.join(
        path,
        'robot_description'
    )

    if not pathlib.Path(xacro_file).exists():
        exc = 'Launch file ' + xacro_file + ' does not exist'
        raise Exception(exc)
    
    mapping = {}
    if to_bool(use_world_ned):
        mappings={'debug': debug, 'namespace': namespace, 'inertial_reference_frame':'world_ned'}
    else:
        mappings={'debug': debug, 'namespace': namespace, 'inertial_reference_frame':'world'}
    
    doc = xacro.process(xacro_file, mappings=mappings)
         
    with open(output, 'w') as file_out:
        file_out.write(doc)
    
    # URDF spawner
    args=('-gazebo_namespace /gazebo '
        '-x %s -y %s -z %s -R %s -P %s -Y %s -entity %s -file %s' 
        %(x, y, z, roll, pitch, yaw, namespace, output)).split()

    # Urdf spawner. NB: node namespace does not prefix the topic, 
    # as using a leading /
    urdf_spawner = Node(
        name = 'urdf_spawner',
        package='gazebo_ros',
        executable='spawn_entity.py',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        # TODO To replace in foxy with parameters=[{'robot_description', Command('ros2 run xacro...')}]
        arguments=args
    )

    # A joint state publisher plugin already is started with the model, no need to use the default joint state publisher

    args = (output).split()
    robot_state_publisher = Node(
        name = 'robot_state_publisher',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        # TODO To replace in foxy with parameters=[{'robot_description', Command('ros2 run xacro...')}]
        arguments=args,
        output = 'screen',
        parameters=[{'use_sim_time': use_sim_time}] # Use subst here
    )

    # Message to tf
    message_to_tf_launch = os.path.join(
        get_package_share_directory('uuv_assistants'),
        'launch',
        'message_to_tf.launch'
    )

    if not pathlib.Path(message_to_tf_launch).exists():
        exc = 'Launch file ' + message_to_tf_launch + ' does not exist'
        raise Exception(exc)

    launch_args = [('namespace', namespace), ('world_frame', 'world'), 
            ('child_frame_id', '/' + namespace + '/base_link')]
    message_to_tf_launch = IncludeLaunchDescription(
            AnyLaunchDescriptionSource(message_to_tf_launch), launch_arguments=launch_args)

   
    group = GroupAction([
        PushRosNamespace(namespace), 
        urdf_spawner, 
        robot_state_publisher,
    ])
    

    actions = [global_sim_time, gazebo_world, group, message_to_tf_launch]
    if enable_control_interface:
        actions.append(control_launch)

    return actions

# =============================================================================
def generate_launch_description():
    # TODO Try LaunchContext ?
    return LaunchDescription([
        DeclareLaunchArgument('debug', default_value='0'),

        DeclareLaunchArgument('x', default_value='15'),
        DeclareLaunchArgument('y', default_value='-15'),
        DeclareLaunchArgument('z', default_value='-3'),
        DeclareLaunchArgument('roll', default_value='0.0'),
        DeclareLaunchArgument('pitch', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),

        DeclareLaunchArgument('mode', default_value='default'),
        DeclareLaunchArgument('namespace', default_value='tardigrade'),
        DeclareLaunchArgument('use_ned_frame', default_value='false'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('paused', default_value='false'),
        DeclareLaunchArgument('headless', default_value='false'),
        DeclareLaunchArgument('verbose', default_value='true'),
        DeclareLaunchArgument('enable_control_interface', default_value='true'),
        DeclareLaunchArgument('control_interface', default_value='cmd_vel'),

        OpaqueFunction(function = launch_setup)
    ])