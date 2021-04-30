#!/bin/bash

# please specify the daily build docker images URL, e.g.
#http://121.36.84.172/dailybuild/openEuler-20.03-LTS-SP2/openeuler-2021-05-08-12-45-27/docker_img/aarch64/openEuler-docker.aarch64.tar.xz
BASE_IMG_URL="dailybuild docker images URL"

cd `dirname $0`
curl -L $BASE_IMG_URL | docker load
docker build . -t openeuler-pkg-build
