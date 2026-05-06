from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    pkg_share = get_package_share_directory('surgical_description')
    gazebo_pkg = get_package_share_directory('gazebo_ros')

    world = LaunchConfiguration('world')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_share, 'worlds', 'surgical_world.world'),
        description='Full path to world file'
    )

    xacro_file = os.path.join(pkg_share, 'urdf', 'surgical_robot.urdf.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),
        value_type=str
    )

    return LaunchDescription([

        declare_world,

        # Proper Gazebo Launch
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world}.items(),
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),

        # Spawn Robot
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'surgical_robot',
                '-z', '0.2'
            ],
            output='screen'
        ),

    ])