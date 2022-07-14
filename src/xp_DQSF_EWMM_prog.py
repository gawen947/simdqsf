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

SIXP_DELAY    = 2
ALPHA         = 0.1
ALPHA0        = 0.3
ALPHA1        = 0.01
OVERPROVISION = 1
OVERPROVISION_CELLS = 1
OVERPROVISION_TXQ   = math.floor(0.7*sim.MAX_TXQ)


MAX_ITER = 86400

PERIOD_DURATION=120
AMPLITUDE=6
BASE=2
BASE_WAIT_TIME=3600
EPSILON=0.1

print("# growth start at", BASE_WAIT_TIME)
print("# growth end at", BASE_WAIT_TIME + PERIOD_DURATION*AMPLITUDE)
TRAFFIC_PATTERN = []
for i in range(BASE_WAIT_TIME):
  TRAFFIC_PATTERN.append(BASE)

# Our growth in traffic is linear (so give us a fractional number)
# but the scheduling function only deals with discrete amount of traffic
# (there is no such thing as half a packet). Thus wee need a mechanism
# to transform this fractional traffic in a linear one.
avg_traffic=BASE
current_traffic=BASE
for i in range(BASE_WAIT_TIME, BASE_WAIT_TIME + PERIOD_DURATION*AMPLITUDE):
  real_traffic = BASE + float((i - BASE_WAIT_TIME)) / (PERIOD_DURATION)

  if abs(current_traffic - real_traffic) > EPSILON:
    if current_traffic < real_traffic:
      current_traffic += 1
    else: # current_traffic > real_traffic
      current_traffic -= 1

  TRAFFIC_PATTERN.append(current_traffic)


for i in range(BASE_WAIT_TIME + PERIOD_DURATION*AMPLITUDE, MAX_ITER):
  TRAFFIC_PATTERN.append(BASE + AMPLITUDE)

# Compare with MSF legacy
#schedfun = SF_MSF_Legacy.SchedulingFunction(0.25, 0.75, 100)

# The last iteration EWMM BUDGET2
schedfun   = SF_DQSF_EWMM_BUDGET2.SchedulingFunction(ALPHA0, ALPHA1, OVERPROVISION_CELLS, OVERPROVISION_TXQ, show_alloc=True)
#schedfun   = SF_DQSF_EWMA.SchedulingFunction(ALPHA, OVERPROVISION)

# Our previous implementation
#schedfun   = SF_DQSF_1SF.SchedulingFunction(ALPHA, OVERPROVISION)
simulation = sim.Simulation(len(TRAFFIC_PATTERN), SIXP_DELAY, TRAFFIC_PATTERN, schedfun, sim.PrintPlot)

for _ in simulation:
  pass
