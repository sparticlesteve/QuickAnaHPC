#!/bin/bash

# Launch N jobs and set environment variable TASKID 0-N
numTasks=79
tasksPerNode=24
image=chos:atlas_nocondb_uc_cmssl6cbase_sqsh_v5

for (( i=0; i < $numTasks; i+=$tasksPerNode )); do
    taskStart=$i
    taskEnd=$((taskStart + tasksPerNode))
    echo "Submitting tasks $taskStart-$taskEnd"
    vars="TASK_ID_START=$taskStart,TASKS_PER_NODE=$tasksPerNode,NUM_TASKS=$numTasks,SHIFTER=$image"
    qsub -v $vars edison_submit.pbs
done
