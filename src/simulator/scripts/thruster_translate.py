#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from uuv_gazebo_ros_plugins_msgs.msg import FloatStamped

class ThrusterTranslate(Node):
    def __init__(self):
        super().__init__('thruster_translate')

        self.sub = self.create_subscription(Float64MultiArray, '/tardigrade/thrusts', self.translate, 10)
        self.thrusts = []
        for i in range(8):
            pub = self.create_publisher(FloatStamped, f'/tardigrade/thrusters/id_{i}/input', 10)
            self.thrusts.append(pub)
        
    def translate(self, msg: Float64MultiArray):
        for i in range(8):
            out = FloatStamped()
            out.header.stamp = self.get_clock().now().to_msg()
            out.data = float(msg.data[i])
            self.thrusts[i].publish(out)

def main(args=None):
    rclpy.init(args=args)
    translator = ThrusterTranslate()
    rclpy.spin(translator)
    rclpy.shutdown()

if __name__=='__main__':
    main()