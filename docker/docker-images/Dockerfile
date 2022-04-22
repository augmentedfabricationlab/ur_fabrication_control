# Build:
#  docker build --rm -f Dockerfile -t gramaziokohler/ros-rfl-planner .
#
# Usage:
#  docker pull gramaziokohler/ros-rfl-planner

FROM gramaziokohler/ros-kinetic-moveit:latest
LABEL maintainer "Gido Dielemans <gido.dielemans@tum.de>"

SHELL ["/bin/bash","-c"]
ENV CATKIN_WS=/root/catkin_ws
RUN mkdir -p $CATKIN_WS/src

COPY . /root/catkin_ws/src

# Add robot packages to local catkin workspace
RUN echo "Building tools for ROS" \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    # Update apt-get because its cache is always cleared after installs to keep image size down
    && apt-get update \
    # abb packages
    && git clone https://github.com/augmentedfabricationlab/robotic_setups_description.git \
    # Install dependencies
    && cd $CATKIN_WS \
    && rosdep install -y --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} \
    # Build catkin workspace
    && catkin_make \
    && rm -rf /var/lib/apt/lists/*
