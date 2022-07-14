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
import math

# Works well with not too bursty traffic.
# For instance:
#  TRAFFIC_PATTERN = [6, 0, 4, 3, 2, 1, 5, 0, 0, 0] + [0]*300
#  This is OK and it estimates the average correctly. There is no recurring drop.
#  TRAFFIC_PATTERN = [6, 7, 4, 3, 2, 1, 5, 0, 0, 0] + [0]*300
#  This is too bursty! Always drop packets and thus constantly tries new allocations.
#  This is caused by the fact that it estimates the average number of unused cells
#  and doesn't see that this "average" is not available for each point in time.

class SchedulingFunction(sim.SchedulingFunction):
  def __init__(self, alpha, overprovision):
    # params
    self.alpha = alpha
    self.overprovision = overprovision

    # metrics
    self.ewma_dq = 0.0
    self.ewma_u  = 0.0

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame
    dq = txq - old_txq

    self.ewma_dq = sim.ewma(self.ewma_dq, dq, self.alpha)
    self.ewma_u  = sim.ewma(self.ewma_u, sframe.get_cells_unused(), self.alpha)

    if drop > 0:
      self.ewma_dq += drop # immediately allocate cells
      self.ewma_u   = 0 # we are in a state of dropping queues, we must learn the unused state again

    rounded_ewma_dq = round(self.ewma_dq)
    rounded_ewma_u  = math.floor(self.ewma_u)

    decision = 0
    if rounded_ewma_dq > 0:
      decision = rounded_ewma_dq
      # mark the average for the fact that we did some allocation
      # to avoid multiple allolscations because of 6P delay
      self.ewma_dq -= decision
    elif rounded_ewma_u > self.overprovision:
      decision = -(rounded_ewma_u - self.overprovision)
      # mark the average for the fact that we did some deallocation
      # to avoid multiple deallocations because of 6P delay
      self.ewma_u += decision

    return {
      "ewma_dq" : self.ewma_dq,
      "ewma_u"  : self.ewma_u,
      "decision": decision
    }

  def schema(self):
    return ["ewma_dq", "ewma_u", "decision"]