#!/bin/bash
protoc -I=worldengine --python_out=worldengine/protobuf worldengine/World.proto