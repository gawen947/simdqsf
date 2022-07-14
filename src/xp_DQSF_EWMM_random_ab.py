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

random.seed(1234)
TRAFFIC_PATTERN = [ random.randint(0, 6) for i in range(MAX_ITER) ]

def print_legend():
  print("# alpha beta    total_sixp total_drop total_traffic    total_cells total_unused_cells total_used_cells    pct_sixp pct_drop pct_unused_cells pct_used_cells")

def print_stats(alpha, beta, simulation):
  total_sixp       = simulation.sframe.total_sixp_requests()
  pct_sixp         = (100. * total_sixp) / simulation.total_traffic
  pct_drop         = (100. * simulation.total_drop) / simulation.total_traffic
  pct_unused_cells = (100. * simulation.total_unused_cells) / simulation.total_cells
  pct_used_cells   = (100. * simulation.total_used_cells) / simulation.total_cells
  print(f"{alpha} {beta}    {total_sixp} {simulation.total_drop} {simulation.total_traffic}    {simulation.total_cells} {simulation.total_unused_cells} {simulation.total_used_cells}    {pct_sixp} {pct_drop} {pct_unused_cells} {pct_used_cells}")

def test_traffic(alpha, beta):
  # The last iteration EWMM BUDGET2
  schedfun   = SF_DQSF_EWMM_BUDGET2.SchedulingFunction(alpha, beta, OVERPROVISION_CELLS, OVERPROVISION_TXQ)
  simulation = sim.Simulation(MAX_ITER, SIXP_DELAY, TRAFFIC_PATTERN, schedfun, sim.PrintNull)

  for _ in simulation:
    pass

  print_stats(alpha, beta, simulation)

DEFAULT_ALPHA = ALPHA0
DEFAULT_BETA  = ALPHA1

print_legend()

# change alpha
alpha_0    = 0.01
alpha_step = 0.01
print("# ==== change alpha ====")
for i in range(100):
  alpha = alpha_0 + i * alpha_step
  beta  = DEFAULT_BETA
  test_traffic(alpha, beta)
print("# ==== change beta ====")
beta_0    = 0.0005
beta_step = 0.0005
for i in range(200):
  alpha = DEFAULT_ALPHA
  beta  = beta_0 + i * beta_step
  test_traffic(alpha, beta)
