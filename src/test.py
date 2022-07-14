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
ALPHA         = 0.01
ALPHA0        = 0.01
ALPHA1        = 0.005
OVERPROVISION = 1
OVERPROVISION_CELLS = 1
OVERPROVISION_TXQ   = math.floor(0.7*sim.MAX_TXQ)


MAX_ITER = 200000

#TRAFFIC_PATTERN = [6, 0, 4, 3, 2, 1, 5, 0, 0, 0]
#TRAFFIC_PATTERN = [6, 8, 4, 3, 4, 1, 5, 0, 0, 0] + [0]*300
#TRAFFIC_PATTERN = [6, 0]
TRAFFIC_PATTERN = [6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6]
#TRAFFIC_PATTERN = [4] + [0]*100
#TRAFFIC_PATTERN = [1] + [0]*300 => doesn't work very well :( )

# Compare with MSF legacy
#schedfun = SF_MSF_Legacy.SchedulingFunction(0.25, 0.75, 100)

# This one works
schedfun   = SF_DQSF_EWMM_BUDGET2.SchedulingFunction(ALPHA0, ALPHA1, OVERPROVISION_CELLS, OVERPROVISION_TXQ)

#schedfun   = SF_DQSF_EWMM_TXQ.SchedulingFunction(ALPHA0, ALPHA1, OVERPROVISION)
#schedfun   = SF_DQSF_EWMA.SchedulingFunction(ALPHA, OVERPROVISION)
#schedfun   = SF_DQSF_1SF.SchedulingFunction(ALPHA, OVERPROVISION)
simulation = sim.Simulation(MAX_ITER, SIXP_DELAY, TRAFFIC_PATTERN, schedfun, sim.PrintHuman)

for _ in simulation:
  pass
