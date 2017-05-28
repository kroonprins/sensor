#!/bin/bash

rootdir=/home/pi
logfile=${rootdir}/logs/application.log

PYTHONPATH=${rootdir}/lib
export PYTHONPATH

export APPLICATION_LOG_LEVEL=20 #INFO

python2 ${rootdir}/main.py >> ${logfile} 2>&1 &