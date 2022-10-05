#!/bin/sh
docker build . -t golem-measure-download-time:latest;
gvmkit-build golem-measure-download-time:latest;
gvmkit-build golem-measure-download-time:latest --push;
