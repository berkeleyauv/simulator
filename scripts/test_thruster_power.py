import rospy
from std_msgs.msg import Float32
from uuv_gazebo_ros_plugins_msgs.msg import FloatStamped
from random import random

THRUSTER_ID = '0'
THRUSTER_POWER = 1000

rospy.init_node('test_setter')
pub_thrust = rospy.Publisher('/urab_sub/thrusters/' + THRUSTER_ID + '/input', FloatStamped, queue_size=10)
rate = rospy.Rate(1)

while not rospy.is_shutdown():
    msg = FloatStamped()
    msg.header.stamp = rospy.Time.now()
    msg.data = THRUSTER_POWER
    pub_thrust.publish(msg)
    rate.sleep()
