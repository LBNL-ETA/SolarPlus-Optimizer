FROM ubuntu:16.04

# Install required packages with root
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    git

# Create non-root user
# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/developer && \
    mkdir -p /etc/sudoers.d && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer
USER developer
ENV HOME /home/developer

# Install python3 packages
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --user \
    pandas==0.23.4 \
    flask \
    pyxbos \
    pymortar \
    pyyaml

WORKDIR $HOME