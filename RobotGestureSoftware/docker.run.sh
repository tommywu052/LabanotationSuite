#!/bin/bash

docker run -it --rm --network=host \
       -e DISPLAY=$DISPLAY \
       -e QT_X11_NO_MITSHM=1 \
       -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
       stratpro:LabanSuite
