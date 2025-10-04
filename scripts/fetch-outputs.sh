#!/bin/bash

# $1 = <ruta-completa-a-la-carpeta-del-trabajo>
# $2 = <ip-del-submitter>
# $3 = <job-id>

if [ $# -ne 3 ]; then
    echo "Usage: $0 <job-folder-path> <submitter-ip> <job-id>"
    exit 1
fi

# Check if local folder exists
if [ ! -d "$1" ]; then
    echo "Error: Local folder '$1' does not exist"
    exit 1
fi

echo "Waiting for job output..."

while true; do
    ssh -i ~/.ssh/parallel alma@$2 "[ -e \"/tmp/$3/job_0.out\" ]"
    STATUS=$?
    
    if [ $STATUS -eq 0 ]; then
        echo "Job output found!"
        break
    fi
    
    echo "Still waiting... (checking every 5 seconds)"
    sleep 5
done

echo "Copying results back..."
scp -i ~/.ssh/parallel alma@$2:/tmp/$3/* "$1/"

echo "Results copied successfully!"