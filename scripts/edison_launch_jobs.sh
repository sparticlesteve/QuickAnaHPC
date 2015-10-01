#!/bin/bash

# Launch N jobs and set environment variable TASKID 0-N
N=10
image=chos:atlas_nocondb_uc_cmssl6cbase_sqsh_v4

for (( i=0; i < $N; i++ )); do
    echo "Submitting job $i"
    qsub -v TASKID=$i,NUMTASKS=$N,SHIFTER=$image edison_submit.pbs
done
