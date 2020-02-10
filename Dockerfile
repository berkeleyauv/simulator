FROM ros:melodic-ros-core
# place here your application's setup specifics
RUN apt-get update && apt update \
	&& apt-get install x11vnc -y \
	&& apt install xvfb -y \
	&& apt install ros-melodic-uuv-simulator -y \
	&& apt-get install python-catkin-tools -y

# Create catkin workspace
# TODO: pull the ur@b simulator GitHub repo in this
RUN /bin/bash -c 'source /opt/ros/$ROS_DISTRO/setup.bash >> ~/.bashrc \
	&& mkdir -p "$HOME/catkin_ws/src" \
	&& cd "$HOME/catkin_ws/src" \
	&& catkin_init_workspace \
	&& cd "$HOME/catkin_ws" \
	&& catkin build'

ENV DISPLAY :1.0
ENV GAZEBO_MODEL_PATH /root/catkin_ws/src/urab_sim/vortex_descriptions/world_models:

# Keep the docker running and source relevant files on docker run
CMD /bin/bash -c "source /root/.bashrc && tail -f /dev/null"

# You need to do the below to do roslaunch
# source ~/catkin_ws/devel/setup.bash >> ~/.bashrc'

