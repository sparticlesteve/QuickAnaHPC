#!/bin/bash

# Setup environment
source edison_cvmfs_setup.sh

set -e

# Configure the job
scanDir=$SCRATCH/xAOD
jobDirBase=$SCRATCH/outputs/$PBS_JOBNAME.$PBS_JOBID

#otherOpts="--noSysts --maxEvents 5000"
#otherOpts="--noSysts --maxEvents 1000 --splitSamples"
otherOpts="--splitSamples --opt"

# Calculate task range
TASK_ID_END=$((TASK_ID_START + TASKS_PER_NODE))
if [ $TASK_ID_END -ge $NUM_TASKS ]; then
    TASK_ID_END=$NUM_TASKS
fi

# Loop over my assigned tasks
for (( i = $TASK_ID_START; i < $TASK_ID_END; i++ )); do
    echo "Starting task $i out of $NUM_TASKS"
    jobDir=$jobDirBase.$i
    # Run the QuickAnaHPC job in the background
    runQuickAnaHPC.py --jobDir $jobDir \
                      --task $i:$NUM_TASKS \
                      --scanDir $scanDir \
                      $otherOpts &
    pids="$pids $!"
done

# Wait for all processes to finish
for pid in $pids; do
    wait $pid
done

echo "All processes have finished"
