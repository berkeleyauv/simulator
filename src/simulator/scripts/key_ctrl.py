#!/usr/bin/env python3

import select
import sys
import termios
import tty

import rclpy
from geometry_msgs.msg import Accel, Twist
from rclpy.node import Node


class KeyCtrl(Node):
    def __init__(self):
        super().__init__('key_ctrl')

        self.declare_parameter('namespace', 'tardigrade')
        self.declare_parameter('interface', 'cmd_vel')
        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('linear_step', 0.4)
        self.declare_parameter('vertical_step', 0.25)
        self.declare_parameter('yaw_step', 0.5)

        namespace = self.get_parameter('namespace').value
        interface = self.get_parameter('interface').value
        self.linear_step = float(self.get_parameter('linear_step').value)
        self.vertical_step = float(self.get_parameter('vertical_step').value)
        self.yaw_step = float(self.get_parameter('yaw_step').value)

        if interface not in ('cmd_vel', 'cmd_accel'):
            raise ValueError("Parameter 'interface' must be 'cmd_vel' or 'cmd_accel'")

        self.interface = interface
        self.topic = f'/{namespace}/{interface}'

        if self.interface == 'cmd_vel':
            self.publisher = self.create_publisher(Twist, self.topic, 10)
        else:
            self.publisher = self.create_publisher(Accel, self.topic, 10)

        # self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info('Publishing %s commands on %s' % (self.interface, self.topic))
        self.get_logger().info(
            'Controls: W/S forward/back, A/D left/right, Q/E yaw left/right, Z/C dive/rise, SPACE stop, Ctrl-C exit'
        )

        # period = 1.0 / max(float(self.get_parameter('publish_rate').value), 1.0)
        # self.timer = self.create_timer(period, self._tick)

    # def _read_key(self):
    #     tty.setraw(sys.stdin.fileno())
    #     rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
    #     key = sys.stdin.read(1) if rlist else ''
    #     termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
    #     return key

    def _build_message(self, key):
        lin_x = 0.0
        lin_y = 0.0
        lin_z = 0.0
        yaw_z = 0.0

        if key == 'w':
            lin_x = self.linear_step
        elif key == 's':
            lin_x = -self.linear_step
        elif key == 'a':
            lin_y = self.linear_step
        elif key == 'd':
            lin_y = -self.linear_step
        elif key == 'q':
            yaw_z = self.yaw_step
        elif key == 'e':
            yaw_z = -self.yaw_step
        elif key == 'z':
            lin_z = -self.vertical_step
        elif key == 'c':
            lin_z = self.vertical_step
        else:
            return Twist() if self.interface == 'cmd_vel' else Accel()

        if self.interface == 'cmd_vel':
            msg = Twist()
        else:
            msg = Accel()

        msg.linear.x = lin_x
        msg.linear.y = lin_y
        msg.linear.z = lin_z
        msg.angular.z = yaw_z

        return msg

    # def _tick(self):
    #     key = self._read_key()

    #     if key == '\x03':
    #         self._publish_zero()
    #         raise KeyboardInterrupt

    #     msg = self._build_message(key)
    #     self.publisher.publish(msg)

    def _publish_zero(self):
        if self.interface == 'cmd_vel':
            msg = Twist()
        else:
            msg = Accel()
        self.publisher.publish(msg)



def main(args=None):
    rclpy.init(args=args)

    node = KeyCtrl()
    try:
        while(1):
            key = input().strip().lower()
            cmd = node._build_message(key)
            node.publisher.publish(cmd)
    except KeyboardInterrupt:
        node.get_logger().info('Stopping key_ctrl')
    finally:
        node._publish_zero()
        # termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
