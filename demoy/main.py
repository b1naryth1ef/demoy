#!/usr/bin/env python
import os, sys, time
import logging

from demo import Demo

logging.basicConfig(
    level=logging.DEBUG
)

if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        Demo.from_file(f).parse()
