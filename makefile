IMG_NAME=mpcpy_master

COMMAND_RUN=docker run \
	  --name solarplusoptimizer \
	  --detach=false \
	  -e DISPLAY=${DISPLAY} \
	  -v /tmp/.X11-unix:/tmp/.X11-unix \
	  --rm \
	  -v `pwd`:/mnt/shared \
	  -i \
          -t \
	  ${IMG_NAME} /bin/bash -c

run:
	$(COMMAND_RUN) \
            "cd /mnt/shared && bash"
