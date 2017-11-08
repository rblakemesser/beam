#!/bin/bash

PROCS=$(ps aux | grep beam.py | wc -l)
if [ $PROCS -lt 2 ]
then
    /home/pi/workspace/beam/venv/bin/python /home/pi/workspace/beam/beam.py
fi
