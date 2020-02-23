FROM ros:melodic-ros-core

# Install VNC and UUV Simulator packages
RUN apt-get update && apt update \
	&& apt-get install x11vnc -y \
	&& apt install xvfb -y \
	&& apt install ros-melodic-uuv-simulator -y \
	&& apt-get install python-catkin-tools -y \
	&& apt-get install vim -y

# Create catkin workspace
RUN /bin/bash -c 'source /opt/ros/$ROS_DISTRO/setup.bash \
	&& mkdir -p "$HOME/catkin_ws/src" \
	&& cd "$HOME/catkin_ws/src" \
	&& catkin_init_workspace \
	&& cd "$HOME/catkin_ws" \
	&& catkin build'

# Put the git repo in the container
ADD . /root/catkin_ws/src

# Build the custom world and model descriptions
RUN cd $HOME/catkin_ws/src \
	&& catkin build \
	&& echo source /opt/ros/$ROS_DISTRO/setup.bash >> ~/.bashrc \
	&& echo source ~/catkin_ws/devel/setup.bash >> ~/.bashrc

# Set some environment variables
ENV DISPLAY :0.0
ENV GAZEBO_MODEL_PATH /root/catkin_ws/src/descriptions/vortex_descriptions/world_models:/root/catkin_ws/src/descriptions/vortex_descriptions/models

# Source relevant files and keep the docker running after "docker run ..." is run
CMD /bin/bash -c "tail -f /dev/null"
