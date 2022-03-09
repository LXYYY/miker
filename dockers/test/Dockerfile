FROM ubuntu:20.04

# install packages
RUN apt-get update && apt-get install -q -y --no-install-recommends \
    dirmngr \
    gnupg2 \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# setup keys
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654

# setup sources.list
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

# setup environment
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# ros-base
# install bootstrap tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    python-rosdep \
    python-rosinstall \
    python-vcstools \
    && rm -rf /var/lib/apt/lists/*

ARG ROS_VERSION=noetic
ENV ROS_DISTRO=$ROS_VERSION

# bootstrap rosdep
RUN rosdep init && \
  rosdep update --rosdistro $ROS_DISTRO


RUN apt-get update && apt-get install -y --no-install-recommends \
ros-${ROS_DISTRO}-perception \
&& rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 lxy \
    && useradd --uid 1000 --gid 1000 -m lxy \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME
RUN usermod -a -G dialout lxy
RUN yes lxy | passwd lxy

RUN apt update && apt install -y ssh && apt clean && ( \
    echo 'LogLevel DEBUG2'; \
    echo 'PermitRootLogin yes'; \
    echo 'PasswordAuthentication yes'; \
    echo 'Subsystem sftp /usr/lib/openssh/sftp-server'; \
  ) > /etc/ssh/sshd_config_test_clion 

COPY /home/mikexyl/Workspaces/miker_ws/miker/entrypoints/ros_entrypoint.sh /

CMD sshd

