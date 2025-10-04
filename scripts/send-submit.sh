#!/bin/bash

# $1 = <ruta-completa-a-la-carpeta-del-trabajo>
# $2 = <ip-del-submitter>
# $3 = <nombre-carpeta-remota>

if [ $# -ne 3 ]; then
    echo "Usage: $0 <job-folder-path> <submitter-ip> <remote-folder-name>"
    exit 1
fi

# Check if the job folder exists
if [ ! -d "$1" ]; then
    echo "Error: Job folder '$1' does not exist"
    exit 1
fi

echo "Copying job files to submitter..."
scp -r -i ~/.ssh/parallel "$1" alma@$2:/tmp/"$3"

echo "Submitting HTCondor job..."
ssh -i ~/.ssh/parallel alma@$2 "cd /tmp/$3 && condor_submit job.sub"

echo "Job submitted successfully!"
