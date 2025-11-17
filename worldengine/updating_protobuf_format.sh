#!/usr/bin/env bash

# Script to regenerate Python protobuf code from World.proto
# Requires: protoc >= 3.19.0

set -e

if ! command -v protoc &> /dev/null; then
    echo "Error: protoc is not installed."
    echo "Please install protobuf compiler:"
    echo "  macOS: brew install protobuf"
    echo "  Linux: sudo apt-get install protobuf-compiler"
    echo "  or download from: https://github.com/protocolbuffers/protobuf/releases"
    exit 1
fi

PROTOC_VERSION=$(protoc --version | awk '{print $2}')
echo "Using protoc version: ${PROTOC_VERSION}"

protoc World.proto --python_out=protobuf

echo "Successfully regenerated protobuf/World_pb2.py"
