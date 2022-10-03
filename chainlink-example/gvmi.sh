#!/bin/sh
docker build . -t chainlink-request-example:latest;
gvmkit-build chainlink-request-example:latest --push;
