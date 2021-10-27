ARG EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest
FROM $EE_BASE_IMAGE

USER root
RUN yum install make -y

USER 1000
