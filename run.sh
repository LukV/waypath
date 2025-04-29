#!/bin/bash

if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

IMAGE_ID=$(docker build -q .)

docker run \
    --rm \
    --publish 8000:8000 \
    $INTERACTIVE \
    "$IMAGE_ID" \
    "$@"
