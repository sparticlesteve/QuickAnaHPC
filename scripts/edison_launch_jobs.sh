#!/bin/bash

# Job submission and configuration options
numTasks=192
tasksPerNode=24
image=chos:atlas_nocondb_uc_cmssl6cbase_sqsh_v5

for (( i=0; i < $numTasks; i+=$tasksPerNode )); do
    taskStart=$i
    taskEnd=$((taskStart + tasksPerNode))
    echo "Submitting tasks $taskStart-$taskEnd"
    vars="TASK_ID_START=$taskStart,TASKS_PER_NODE=$tasksPerNode,NUM_TASKS=$numTasks"
    vars="$vars,SHIFTER=$image"
    qsub -v $vars edison_submit.pbs
done
