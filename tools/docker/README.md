## Dockerfile for basic environment for running tools

This Dockerfile is for quickly building a environment for running the tools.

0. Check the `openEuler.repo`, replace the content with suitable URLs.

1. Run `build-img.sh` script to build Docker image, you need to specify the
   openEuler base image URL with `BASE_IMG_URL` env variable.

2. Use `openeuler-pkg-build` Docker image to build environment for running tools
