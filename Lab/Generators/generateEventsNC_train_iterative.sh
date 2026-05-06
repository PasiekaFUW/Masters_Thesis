#!/bin/bash

Events=1000000  # 1 million events per chunk

BaseProcess="nu_tau_NC"
Sigma="/scratch1/gjedrzej/Lab/splines_3_6_02_Pythia8/splines_3_06_02_nuTau_Ar40_80_P8.xml"

mkdir -p data/NC_samples

echo "Launching 12 parallel GENIE generation jobs..."

for i in {1..12}; do
    # Calculate seed: i=1 -> 4200, i=2 -> 4210, etc.
    Seed=$(( 4290 + i * 10 ))
    Process="${BaseProcess}_${i}"
    
    echo "Starting chunk $i with seed $Seed..."
    
    # Run each gevgen in the background with '&'
    # We pipe the output of each to its own text log so they don't overwrite each other
    gevgen -n $Events \
           -e 0.5,30 \
           -p 16 \
           --cross-sections $Sigma \
           -t 1000180400 \
           -f flux_dune_neutrino_FD.root,nutau_fluxosc \
           --event-generator-list NC \
           --message-thresholds $GENIE/config/Messenger_laconic.xml \
           --mc-job-status-refresh-rate 100 \
           --seed $Seed \
           -o "data/NC_samples/${Process}_interactions.root" > /dev/null 2>&1 &

    # Sleep for a few seconds just to stagger their startup (gentler on the CPU/Disk)
    sleep 5
done

echo "All 6 generation jobs have been successfully submitted to the background!"
echo "Check their progress by typing: ps aux | grep gevgen"