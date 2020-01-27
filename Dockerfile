FROM ros:melodic-ros-core
# place here your application's setup specifics
RUN apt-get update && apt update \
	&& apt-get install x11vnc -y \
	&& apt install xvfb -y \
	&& apt install ros-melodic-uuv-simulator -y \
	&& apt-get install python-catkin-tools -y

ENV DISPLAY :1.0


# Keep the docker running
CMD tail -f /dev/null
