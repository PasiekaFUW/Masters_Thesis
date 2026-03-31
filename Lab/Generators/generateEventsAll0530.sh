#!/bin/bash

Events=500000
Process=nu_tau_CC_NC
Sigma=/scratch1/gjedrzej/Lab/splines_3_6_02_Pythia8/splines_3_06_02_nuTau_Ar40_80_P8.xml


echo "Starting generation of $Events events for $Process..."
echo "Using splines: $Sigma"

mkdir -p data

gevgen -n $Events \
       -e 0.5,30 \
       -p 16 \
       --cross-sections $Sigma \
       -t 1000180400 \
       -f flux_dune_neutrino_FD.root,nutau_fluxosc \
       --event-generator-list Default \
       --message-thresholds Messenger_laconic.xml \
       --seed 1556681 \
       -o "data/$Process"_interactions.root

echo "Output saved as data/${Process}_interactions.root"