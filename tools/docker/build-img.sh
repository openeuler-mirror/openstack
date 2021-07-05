#!/bin/bash

# please specify the daily build docker images URL, e.g.
# http://121.36.84.172/dailybuild/openEuler-20.03-LTS-SP2/openeuler-2021-07-05-12-47-12/docker_img/aarch64/openEuler-docker.aarch64.tar.xz

BASE_IMG_URL=""
if [ -z "$BASE_IMG_URL" ]; then
  echo "Please specify openEuler docker image URL with BASE_IMG_URL!"
  exit
fi

cd `dirname $0`
image_ref=$(curl -L $BASE_IMG_URL | docker load)
image_name=${image_ref#*:}

sed -i "s/FROM.*/FROM $image_name/" Dockerfile
docker build . -t openeuler-pkg-build
