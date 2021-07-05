# NOTE: the following image name is the openEuler docker images name from dailybuild,
# may need to modify
FROM openeuler-20.03-lts-next

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY openEuler.repo /etc/yum.repos.d/

RUN yum update -y && yum install -y \
    sudo git tar curl patch shadow-utils make cmake gcc gcc-c++ \
    rpm-build dnf-plugins-core make rpmdevtools wget python3-pip python2-pip

RUN yum update -y && yum install -y python2-wheel openssl-devel libffi-devel python3-devel

RUN sed -i s'/TMOUT=300/TMOUT=300000000000/' /etc/bashrc

RUN rpmdev-setuptree

WORKDIR /root/
RUN git clone https://gitee.com/openeuler/openstack \
    && cd openstack/tools/oos \
    && python3 setup.py develop \
