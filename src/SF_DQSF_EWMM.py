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

# Using EWMM we try to look at the minimum number of unused cells in the past
# to decide if we can deallocate cells or not.
# Of course in bursty situations, and even in non really bad ones,
# we will see that at worst in the past, we had nearly 0 cells unused.
# So we never decide to deallocate, we just keep the number of unused cells at a minimum.
# That does not go well for bursty traffic that could be handled with DQSF EWMA

class SchedulingFunction(sim.SchedulingFunction):
  def __init__(self, alpha0, alpha1, overprovision):
    # params
    self.alpha0 = alpha0
    self.alpha1 = alpha1
    self.overprovision = overprovision

    # metrics
    self.ewma_dq = 0.0
    self.ewma_u  = 0.0
    self.ewmm_n  = 0.0
    self.ewmm_u  = 0.0

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame
    dq = txq - old_txq

    self.ewma_dq = sim.ewma(self.ewma_dq, dq, self.alpha0)
    self.ewma_u  = sim.ewma(self.ewma_u, sframe.get_cells_unused(), self.alpha1)

    # the ewmm only works with maximum
    # I could make it work by sign shenanigans, but I would mess it up.
    # so we use the number of used cells instead
    self.ewmm_n  = sim.ewmm(self.ewmm_n, sframe.get_cells_used(), self.alpha1)
    self.ewmm_u  = sframe.get_cells_allocated() - self.ewmm_n # N = C - U => U = C - N

    if drop > 0:
      self.ewma_dq += drop # immediately allocate cells
      self.ewma_u   = 0 # we are in a state of dropping queues, we must learn the unused state again

    rounded_ewma_dq = math.floor(self.ewma_dq)
    rounded_ewma_u  = math.floor(self.ewma_u)
    rounded_ewmm_u  = math.floor(self.ewmm_u)

    decision = 0
    if rounded_ewma_dq > 0:
      decision = rounded_ewma_dq
      # mark the average for the fact that we did some allocation
      # to avoid multiple allocations because of 6P delay
      self.ewma_dq -= decision
    elif rounded_ewmm_u > self.overprovision:
      decision = -(rounded_ewmm_u - self.overprovision)
      # mark the average for the fact that we did some deallocation
      # to avoid multiple deallocations because of 6P delay
      self.ewmm_n -= decision

    return {
      "ewma_dq" : self.ewma_dq,
      "ewma_u"  : self.ewma_u,
      "ewmm_n"  : self.ewmm_n,
      "ewmm_u"  : self.ewmm_u,
      "decision": decision
    }

  def schema(self):
    return ["ewma_dq", "ewma_u", "ewmm_n", "ewmm_u", "decision"]