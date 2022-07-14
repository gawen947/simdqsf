# BSD 2-Clause License
#
# Copyright (c) 2021-2022, David Hauweele <david@hauweele.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sim
import SF_MSF_Legacy
import SF_DQSF_1SF
import SF_DQSF_EWMA
import SF_DQSF_EWMM
import SF_DQSF_EWMM_TXQ
import SF_DQSF_EWMM_BUDGET2
import SF_Fixed
import math
import random

SIXP_DELAY    = 2
ALPHA         = 0.1
ALPHA0        = 0.1
ALPHA1        = 0.01
OVERPROVISION = 1
OVERPROVISION_CELLS = 1
OVERPROVISION_TXQ   = math.floor(0.7*sim.MAX_TXQ)

MAX_ITER = 86400

def find_highest_cell_usage(name, traffic_pattern):
  highest_nb_cell    = -1
  highest_cell_usage = -1
  for i in range(0, 100):
    sf = SF_Fixed.SchedulingFunction(i)
    s  = sim.Simulation(MAX_ITER, SIXP_DELAY, traffic_pattern, sf, sim.PrintNull)
    for _ in s:
      pass
    if s.total_drop_after3600 == 0:
      highest_nb_cell    = i
      highest_cell_usage = (100. * s.total_used_cells_after3600) / s.total_cells_after3600
      break
  # with one extra cell for overprov
  sf = SF_Fixed.SchedulingFunction(i+1)
  s  = sim.Simulation(MAX_ITER, SIXP_DELAY, traffic_pattern, sf, sim.PrintNull)
  for _ in s:
    pass
  highest_cell_usage_with_1over = (100. * s.total_used_cells_after3600) / s.total_cells_after3600
  # with two
  sf = SF_Fixed.SchedulingFunction(i+2)
  s  = sim.Simulation(MAX_ITER, SIXP_DELAY, traffic_pattern, sf, sim.PrintNull)
  for _ in s:
    pass
  highest_cell_usage_with_2over = (100. * s.total_used_cells_after3600) / s.total_cells_after3600


  print(name, highest_nb_cell, highest_cell_usage, highest_cell_usage_with_1over, highest_cell_usage_with_2over)

print("# pattern highest-nb-cells highest-cell-usage highest-cell-usage-with-1-over")
random.seed(1234)
find_highest_cell_usage("Regular", [6])
find_highest_cell_usage("Periodic", [6, 0])
find_highest_cell_usage("Random", [ random.randint(0, 6) for i in range(MAX_ITER) ])
find_highest_cell_usage("Bursty", [5,5,5,5]+[0]*120)
find_highest_cell_usage("Very-low", [1]+[0]*120)
