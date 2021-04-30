# NOTE: the following image name is the openEuler docker images name from dailybuild,
# may need to modify
FROM openeuler-20.03-lts-sp2

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

COPY openEuler.repo /etc/yum.repos.d/

RUN yum update -y && yum install -y \
    sudo git tar curl patch shadow-utils make cmake gcc gcc-c++ \
    rpm-build dnf-plugins-core make rpmdevtools wget python3-pip python2-pip

RUN yum update -y && yum install -y python2-wheel openssl-devel libffi-devel python3-devel

RUN sed -i s'/TMOUT=300/TMOUT=300000000000/' /etc/bashrc

RUN rpmdev-setuptree

RUN curl -L https://gitee.com/openeuler/openstack/raw/master/tools/pyporter -o /usr/local/bin/pyporter \
    && chmod +x /usr/local/bin/pyporter

RUN pip3 install pandas requests click

WORKDIR /root/rpmbuild
COPY batch-packaging.py ./
COPY projects.csv ./
