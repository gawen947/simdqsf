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

BIG_M = 1000 # should be more like MaxCells + MaxTxQ but this also works

class SchedulingFunction(sim.SchedulingFunction):
  def __init__(self, alpha0, alpha1, overprovision):
    # params
    self.alpha0 = alpha0
    self.alpha1 = alpha1
    self.overprovision = overprovision

    # metrics
    self.ewma_dq = 0.0
    self.ewma_u  = 0.0
    self.ewmm_budget = 0.0

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame
    dq = txq - old_txq

    self.ewma_dq = sim.ewma(self.ewma_dq, dq, self.alpha0)
    self.ewma_u  = sim.ewma(self.ewma_u, sframe.get_cells_unused(), self.alpha1) # for stats purpose only

    # compute the minimum budget we encountered in the past with alpha1 as time period
    txq_left       = sim.MAX_TXQ - txq
    current_budget = BIG_M - (sframe.get_cells_unused() + txq_left)
    self.ewmm_budget = sim.ewmm2(self.ewmm_budget, current_budget, self.alpha1)
    real_ewmm_budget = BIG_M - self.ewmm_budget

    if drop > 0:
      self.ewma_dq += drop # immediately allocate cells

    rounded_ewma_dq     = math.floor(self.ewma_dq)
    rounded_ewmm_budget = math.floor(real_ewmm_budget) # floor(min(U + TxQLeft))

    decision = 0
    if rounded_ewma_dq > 0:
      decision = rounded_ewma_dq
      # mark the average for the fact that we did some allocation
      # to avoid multiple allocations because of 6P delay
      self.ewma_dq -= decision
    elif rounded_ewmm_budget > self.overprovision:
      decision = -(rounded_ewmm_budget - self.overprovision)
      # mark our budget for the fact that we deallocated
      # but it's in reverse because we are against the BIG_M
      # so we go - which is a + because decision is < 0 (not confusing enough?)
      self.ewmm_budget -= 2*decision

    return {
      "ewma_dq" : self.ewma_dq,
      "ewma_u"  : self.ewma_u,
      "ewmm" : self.ewmm_budget,
      "ewmm_budget": real_ewmm_budget,
      "decision": decision
    }

  def schema(self):
    return ["ewma_dq", "ewma_u", "ewmm", "ewmm_budget", "decision"]