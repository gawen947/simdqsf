# SimDQSF

Simulator for the DQSF TSCH distributed scheduling function.
The simulator has a slotframe precision and does not model the exact passing over each cell of the slotframe. This fit with our scheduling function DQSF WMM which only computes its metrics and takes a decision at the end of each slotframe. The simplicity of this model allows to simulate and compare the behavior of scheduling functions over long durations with known traffic patterns.

  * **src/sim.py**: The simulator itself and modelling of the slotframe and 6P requests.
  * **src/SF_***: Implementation of scheduling functions.
  * **src/xp_***: Experiments with the scheduling functions.

The //gnuplot// directory contains additional scripts that we used to plot figures of the SF behavior over each traffic pattern.
