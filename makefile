IMG_NAME=solarplusoptimizer
NETWORK=my-net
COMMAND_RUN=docker run \
          --name mpcpy \
          --detach=false \
          --network=${NETWORK} \
          -e DISPLAY=${DISPLAY} \
          -v /tmp/.X11-unix:/tmp/.X11-unix \
          --rm \
          -v `pwd`:/mnt/shared \
          -i \
          -t \
          ${IMG_NAME} /bin/bash -c

build:
	docker build --no-cache --rm -t ${IMG_NAME} .
	cd controller && make build

remove-image:
	docker rmi ${IMG_NAME}

run:
	cd controller && make stop
	docker network rm my-net
	docker network create ${NETWORK}
	cd controller && make run-network
	$(COMMAND_RUN) \
            "cd /mnt/shared && bash"
	cd controller && make stop
	docker network rm my-net