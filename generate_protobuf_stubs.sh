#!/bin/bash
protoc -I=lands --python_out=lands/protobuf lands/World.proto