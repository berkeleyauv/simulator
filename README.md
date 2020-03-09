# Simulator

This will set up Underwater Robotics @ Berkeley's team simulator.

# Mac Instructions

It's necessary to differentiate between running commands in the Docker container and on your computer. Prepending commands with `container>` will mean it's run inside the container and prepending commands with `local>` will mean it's run outside the container. `docker exec -it urab-sim bash` is used to transition to running commands in the container (introduced later).

For example:
```
container> echo I'm supposed to be run in the container!
local> echo I'm NOT supposed to be run in the container! Run me in terminal without doing anything fancy!
```

## --Installation--

#### Install Docker Desktop
Install from [here](https://docs.docker.com/docker-for-mac/install/). This is for running Gazebo/the simulator in an Ubuntu environment even though you're using Mac. Verify installation with
```
local> docker --version
```

#### Install VNC Viewer for Google Chrome
Install from [here](https://chrome.google.com/webstore/detail/vnc%C2%AE-viewer-for-google-ch/iabmpiboiopbgfabjmgeedhcmjenhbla?hl=en). This is for viewing the GUI generated by the Docker process later.

#### Pull this git repository
```
# cd to a folder where you want to keep this forever
local> git clone https://github.com/berkeleyauv/simulator.git
```

#### Build and start up the Docker image
Build the docker image in the repo and name it urab-sim. This can take 5-10 minutes without cache.
```
local> cd simulator
local> docker build -t urab-sim .
```

## --Starting the simulator--

#### Open Docker Desktop
Search for the application on your computer and let it start up. The icon should appear in your toolbar on the top right.

#### Start the Docker process
Run the docker image to start the docker process while setting up port forwarding from 5900 to 5900 for vnc connections later
```
local> docker run -p 5900:5900 -d -v="/tmp/.ros/:/root/.ros/" --name=urab-sim urab-sim
```

#### Enter a bash session in the Docker container
This will allow you to run commands in terminal as if you had Ubuntu, ROS, Gazebo, and all simulator dependencies installed.

```
local> docker exec -it urab-sim bash
```

#### Set up a VNC display
We've got a handy dandy script for this.

```
container> cd ~/catkin_ws/src
container> ./start_vnc
```
You can ctrl+C out of the text without worry because these processes are started in the background.

#### Start simulating
Use `roslaunch` to start simulating a world. The syntax is `roslaunch <package name> <launch_filename.launch>`. Here's an example that launches the full RoboSub world:

```
container> roslaunch vortex_descriptions robosub_world.launch
```

#### Visualize!
Open VNC Viewer for Google Chrome.
Enter the following information:
```
Address: localhost:5900
Picture Quality: Automatic
```
Click Connect! The unencripted connection is fine ;)


# Ubuntu Instructions

## --Installation--

#### Pull this git repository
```
# cd to a folder where you want to keep this forever
local> git clone https://github.com/berkeleyauv/simulator.git
```

#### Follow the setup instructions from the Dockerfile, but adjust accordingly
Coming soon


## --Starting the simulator--

Use `roslaunch` to start simulating a world. The syntax is `roslaunch <package name> <launch_filename.launch>`. Here's an example that launches the full RoboSub world:

```
container> roslaunch vortex_descriptions robosub_world.launch
```

# Debugging
See the "Simulator Progress" doc in the team Google Drive in the Software/Perception/ folder

# References
[Vortex NTNU's uuv-simulator](https://github.com/vortexntnu/uuv-simulator)

[UUVSimulator](https://uuvsimulator.github.io/)
```
@inproceedings{Manhaes_2016,
    doi = {10.1109/oceans.2016.7761080},
    url = {https://doi.org/10.1109%2Foceans.2016.7761080},
    year = 2016,
    month = {sep},
    publisher = {{IEEE}},
    author = {Musa Morena Marcusso Manh{\~{a}}es and Sebastian A. Scherer and Martin Voss and Luiz Ricardo Douat and Thomas Rauschenbach},
    title = {{UUV} Simulator: A Gazebo-based package for underwater intervention and multi-robot simulation},
    booktitle = {{OCEANS} 2016 {MTS}/{IEEE} Monterey}
}
```
