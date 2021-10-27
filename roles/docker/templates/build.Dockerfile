ARG EE_BASE_IMAGE=quay.io/ansible/ansible-runner:latest
FROM $EE_BASE_IMAGE

USER root
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh

USER 1000
