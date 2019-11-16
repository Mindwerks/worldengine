#! /bin/bash

docker build docker -t worldengine
docker run --rm -v $(git rev-parse --show-toplevel):/opt/worldengine -it worldengine -o output $@
