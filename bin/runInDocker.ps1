docker run -it --rm `
    -v "${PWD}:/workspace" `
    -v "${Env:USERPROFILE}/.ssh:/root/.ssh:ro" `
    -u root `
    quay.io/ansible/awx-ee:0.1.1 /bin/bash
