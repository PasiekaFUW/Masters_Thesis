#!/bin/bash
#This scripts assumes you are inside the container. Run /home/gjedrzej/startGenieCustom.sh
#Positional arguments should be events, process name, and the desired cross section relative path
# Example: ./generateEvents.sh 1000000 "nu_tau" "/scratch1/gjedrzej/Lab/splines_3_6_02_Pythia8/splines_3_06_02_nuTau_Ar40_80_P8.xml"

Events=$1
Process=$2
Sigma=$3

if [ -z "$3" ]; then
    echo "Usage: ./generateEvents.sh <events> <process_name> <spline_path>"
    exit 1
fi

echo "Starting generation of $Events events for $Process..."
echo "Using splines: $Sigma"

mkdir -p data

gevgen -n $Events \
       -e 3.5,50.0 \
       -p 16 \
       --cross-sections $Sigma \
       -t 1000180400 \
       --event-generator-list Default \
       --message-thresholds $GENIE/config/Messenger_laconic.xml \
       --mc-job-status-refresh-rate 500 \
       --seed 12345 \
       -o "data/$Process"_interactions.root

echo "Output saved as data/${Process}_interactions.root"