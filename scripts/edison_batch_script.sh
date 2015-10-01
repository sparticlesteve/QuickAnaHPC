#!/bin/bash

# Setup environment
source edison_cvmfs_setup.sh

# Configure the job
scanDir=/global/scratch2/sd/sfarrell/xAOD
jobDir=$SCRATCH/$PBS_JOBNAME.$PBS_JOBID
nProofWorkers=24

# Run the QuickAnaHPC job
runQuickAnaHPC.py --jobDir $jobDir \
                  --task $TASKID:$NUMTASKS \
                  --scanDir $scanDir \
                  --driver proof --nProofWorkers $nProofWorkers \
                  --splitSamples --opt
