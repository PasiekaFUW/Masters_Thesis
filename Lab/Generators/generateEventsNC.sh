#!/bin/bash

#This scripts assumes you are inside the container. Run /home/gjedrzej/startGenieCustom.sh
#Positional arguments should be events, process name, and the desired cross section relative path
# Example: ./generateEvents.sh 100000 nu_tau /scratch1/gjedrzej/Lab/splines_3_6_02_Pythia8/splines_3_06_02_nuTau_Ar40_80_P8.xml

Events=500000  
Process=nu_tau_NC
Sigma=/scratch1/gjedrzej/Lab/splines_3_6_02_Pythia8/splines_3_06_02_nuTau_Ar40_80_P8.xml

# if [ -z "$3" ]; then
#     echo "Usage: ./generateEvents.sh <events> <process_name> <spline_path>"
#     exit 1
# fi

echo "Starting generation of $Events events for $Process..."
echo "Using splines: $Sigma"

mkdir -p data

gevgen -n $Events \
       -e 0.1,80 \
       -p 16 \
       --cross-sections $Sigma \
       -t 1000180400 \
       -f flux_dune_neutrino_FD.root,nutau_fluxosc \
       --event-generator-list NC \
       --message-thresholds $GENIE/config/Messenger_laconic.xml \
       --mc-job-status-refresh-rate 500 \
       --seed 1556681 \
       -o "data/$Process"_interactions.root

echo "Output saved as data/${Process}_interactions.root"