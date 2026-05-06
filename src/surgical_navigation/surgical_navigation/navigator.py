import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
import yaml


class HospitalNavigator(Node):

    def __init__(self):

        super().__init__('hospital_navigator')

        self.navigator = BasicNavigator()

        db_path = "/home/sreehitha/instrument_robot_ws/src/surgical_navigation/config/instrument_db.yaml"

        with open(db_path, 'r') as file:
            self.instrument_db = yaml.safe_load(file)

        self.get_logger().info("Instrument database loaded")

        self.get_logger().info("Waiting for Nav2...")
        self.navigator.waitUntilNav2Active()

        self.subscription = self.create_subscription(
            String,
            '/surgery_request',
            self.surgery_callback,
            10
        )

        self.get_logger().info("Waiting for surgery request...")

    def create_pose(self, x, y, z_orient):

        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.navigator.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        pose.pose.orientation.z = z_orient
        pose.pose.orientation.w = 1.0

        return pose


    def go_to(self, x, y, z_orient):

        goal = self.create_pose(x, y, z_orient)

        self.get_logger().info("Navigating...")

        self.navigator.goToPose(goal)

        while not self.navigator.isTaskComplete():
            pass

        self.get_logger().info("Reached location")


    def surgery_callback(self, msg):

        surgery = msg.data

        if surgery in self.instrument_db:
            instruments = self.instrument_db[surgery]
        else:
            instruments = []

        self.get_logger().info(f"Instruments required: {instruments}")

        self.get_logger().info(f"Surgery request received: {surgery}")

        instrument_room = (2.34457, -9.67203, 0.72)
        operation_table = (-0.32357, 0.90164, 0.73)
        sterilization_room = (-6.36751, -10.2025, 0.98)

        self.go_to(*instrument_room)

        self.get_logger().info(f"Collecting instruments: {instruments}")

        self.go_to(*operation_table)

        self.get_logger().info("Delivering instruments...")

        self.go_to(*sterilization_room)

        self.get_logger().info("Dropping instruments...")


def main(args=None):

    rclpy.init(args=args)

    node = HospitalNavigator()

    rclpy.spin(node)

    rclpy.shutdown()