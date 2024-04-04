#!/bin/bash 

watch -n 5 "echo 'LAST COMPLETED ITERATION:' ; grep -E 'INFO:root:[0-9]+$' stderr | tail -1 ; echo STDERR: ; tail stderr ; echo RUNTIME: ; squeue -u oyy1 | tail -1"