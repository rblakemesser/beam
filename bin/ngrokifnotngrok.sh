#!/bin/bash

PROCS=$(ps aux | grep ngrok | wc -l)
if [ $PROCS -lt 2 ]
then
    ngrok http -subdomain=blendra 5555
fi
