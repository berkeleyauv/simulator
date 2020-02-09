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
	&& catkin build \
	\
	# Get vortexntnu's robosub components and the latest uuv_simulator components
	&& cd "$HOME/catkin_ws/src" \
	&& git clone https://github.com/vortexntnu/uuv-simulator.git vortex_uuv \
	\
	# Remove vortex (the team's) dependencies
	&& for f in $(find vortex_uuv -type f -name "CMakeLists.txt"); do sed -i 's/vortex//g' $f && sed -i 's/navigation_launch//g' $f; done \
	\
	# Only take the packages to start robosub_world.launch from vortexntnu
	&& mkdir urab_sim \
	&& mv vortex_uuv/uuv_assistants/ urab_sim \
	&& rm vortex_uuv/uuv_descriptions/CMakeLists.txt vortex_uuv/uuv_descriptions/CHANGELOG.rst \
	&& sed -i 's/uuv_descriptions/vortex_descriptions/g' vortex_uuv/uuv_descriptions/package.xml \
	&& cd urab_sim \
	&& catkin_create_pkg vortex_descriptions \
	&& mv ../vortex_uuv/uuv_descriptions/* vortex_descriptions/ \
	&& rm -r ../vortex_uuv/ \
	\
	# Build
	&& cd "$HOME/catkin_ws" \
	&& catkin build \
	&& echo source ~/catkin_ws/devel/setup.bash >> ~/.bashrc'

ENV DISPLAY :1.0
ENV GAZEBO_MODEL_PATH /root/catkin_ws/src/urab_sim/vortex_descriptions/world_models:

# Keep the docker running and source relevant files on docker run
CMD /bin/bash -c "source /root/.bashrc && tail -f /dev/null"
