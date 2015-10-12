#!/bin/bash

# Setup environment
source edison_cvmfs_setup.sh

# Configure the job
scanDir=$SCRATCH/xAOD
jobDirBase=$SCRATCH/outputs/$PBS_JOBNAME.$PBS_JOBID
logDir=$SCRATCH/logs/$PBS_JOBNAME.$PBS_JOBID
mkdir -p $logDir

# Nominal settings with systematics
otherOpts="--splitSamples 170000 --opt"
# Nominal settings without systematics
#otherOpts="--splitSamples 170000 --noSysts"

# Test out sample splitting without running
#otherOpts="--maxEvents 0 --splitSamples 160000"

# Calculate task range
TASK_ID_END=$((TASK_ID_START + TASKS_PER_NODE))
if [ $TASK_ID_END -ge $NUM_TASKS ]; then
    TASK_ID_END=$NUM_TASKS
fi

# Loop over my assigned tasks
for (( i = $TASK_ID_START; i < $TASK_ID_END; i++ )); do
    jobDir=$jobDirBase.$i
    logFile=$logDir/task_$i.log
    echo "Starting task $i out of $NUM_TASKS"
    echo "  Writing outputs to $jobDir"
    echo "  Directing log output to $logFile"
    # Run the QuickAnaHPC job in the background
    runQuickAnaHPC.py --jobDir $jobDir \
                      --task $i:$NUM_TASKS \
                      --scanDir $scanDir \
                      $otherOpts &> $logFile &
    echo "  PID $!"
    pids="$pids $!"
done

# Wait for all processes to finish
set -e
echo "Waiting on processes to finish"
for pid in $pids; do
    wait $pid
    echo "Process $pid has finished"
done

echo "All processes have finished"
