#!/bin/sh
docker build . -t python-web3:latest;
gvmkit-build python-web3:latest;
gvmkit-build python-web3:latest --push;
