ARG EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest
FROM $EE_BASE_IMAGE

RUN yum install make -y
