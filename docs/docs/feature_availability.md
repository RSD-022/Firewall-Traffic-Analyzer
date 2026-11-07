# Feature Availability and Target Leakage Analysis

## Objective

Determine which features can be observed before a firewall
decision and which may only be available during or after
traffic processing.

## Prediction Scenarios

1. Historical log classification:
   Predict actions from recorded completed-flow features.

2. Pre-decision prediction:
   Predict the action using information available before
   the firewall applies its policy.

## Main Finding

High classification accuracy on historical firewall logs
does not necessarily imply successful real-time prediction.

NAT attributes, byte counters, packet counts and session
duration require careful availability analysis.