#!/usr/bin/env python
import os, sys

def build_proto_py():
    """
    Attempts to build all the required protobuf Python
    source files
    """
    print "Building Protobuf Files"

    print "  ensuring destination exists..."
    if not os.path.exists("demoy/pb"):
        print "  creating missing destination path..."
        os.mkdir("demoy/pb")

    print "  transpiling proto files to python..."
    os.system("protoc -I=proto/ --python_out=demoy/pb proto/*.proto")

    print "Finished building protobuf files!"

if __name__ == "__main__":
    build_proto_py()
