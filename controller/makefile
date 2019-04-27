IMG_NAME=datamanager
NETWORK=my-net

COMMAND_RUN=docker run \
	  --name ${IMG_NAME} \
	  --detach=true \
	  --rm \
	  -i \
          -t \
	  -p 127.0.0.1:5000:5000 \
	  ${IMG_NAME}

COMMAND_RUN_NETWORK=docker run \
	  --name ${IMG_NAME} \
	  --network=${NETWORK} \
	  --rm \
 	  -it \


build:
	docker build --no-cache --rm -t ${IMG_NAME} .

remove-image:
	docker rmi ${IMG_NAME}

run:
	$(COMMAND_RUN)
	docker cp . ${IMG_NAME}:/home/developer/datamanager
	docker cp ../data ${IMG_NAME}:/home/developer/datamanager/data
	docker exec -it ${IMG_NAME} /bin/bash -c "cd datamanager && python3 restapi.py"
	docker stop ${IMG_NAME}

run-network:
	$(COMMAND_RUN_NETWORK) --detach=true ${IMG_NAME}
	docker cp . ${IMG_NAME}:/home/developer/datamanager
	docker cp ../data ${IMG_NAME}:/home/developer/datamanager/data
	docker exec --detach ${IMG_NAME} /bin/bash -c "cd datamanager && python3 restapi.py"

stop:
	docker stop ${IMG_NAME}
    