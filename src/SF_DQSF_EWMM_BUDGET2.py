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
  def __init__(self, alpha0, alpha1, overprovision_cells, overprovision_txq, show_alloc=False):
    # params
    self.alpha0 = alpha0
    self.alpha1 = alpha1
    self.overprovision_cells = overprovision_cells
    self.overprovision_txq   = overprovision_txq

    self.show_alloc=show_alloc

    # metrics
    self.ewma_dq   = 0.0
    self.ewma_u    = 0.0
    self.ewmm_u    = 0.0
    self.ewmm_txql = 0.0

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq) :  # TxQ of the last SFrame
    alloc_because_drop = False

    dq       = txq - old_txq
    txq_left = sim.MAX_TXQ - txq

    self.ewma_dq = sim.ewma(self.ewma_dq, dq, self.alpha0)
    self.ewma_u  = sim.ewma(self.ewma_u, sframe.get_cells_unused(), self.alpha1) # for stats purpose only

    # compute the minimum number of cells and TxQLeft we encountered in the past with alpha1 as time period
    self.ewmm_u    = sim.ewmm2(self.ewmm_u, BIG_M - sframe.get_cells_unused(), self.alpha1)
    self.ewmm_txql = sim.ewmm2(self.ewmm_txql, BIG_M - txq_left, self.alpha1)
    #self.ewmm_u    = sim.ewmm(self.ewmm_u, BIG_M - sframe.get_cells_unused(), self.alpha1)
    #self.ewmm_txql = sim.ewmm(self.ewmm_txql, BIG_M - txq_left, self.alpha1)
    real_ewmm_u    = BIG_M - self.ewmm_u
    real_ewmm_txql = BIG_M - self.ewmm_txql

    if drop > 0:
      alloc_because_drop = True
      self.ewma_dq += drop # immediately allocate cells

    rounded_ewma_dq   = round(self.ewma_dq)
    rounded_ewma_u    = math.floor(self.ewma_u)
    rounded_ewmm_u    = math.floor(real_ewmm_u)
    rounded_ewmm_txql = math.floor(real_ewmm_txql)

    decision = 0
    if rounded_ewma_dq > 0:
      decision = rounded_ewma_dq
      # mark the average for the fact that we did some allocation
      # to avoid multiple allocations because of 6P delay
      self.ewma_dq -= decision

      if self.show_alloc:
        if alloc_because_drop:
         print("%d DROP_ALLOC %d" % (iter_idx, decision))
        else:
         print("%d DQ_ALLOC %d" % (iter_idx, decision))
    elif rounded_ewmm_u > self.overprovision_cells:
      decision     = -(rounded_ewmm_u - self.overprovision_cells)
      self.ewmm_u -= decision # mark our budget for the fact that we deallocated
    # elif self.ewma_dq < 0 and real_ewmm_u < 1 and rounded_ewmm_txql > self.overprovision_txq:
    elif rounded_ewmm_txql > self.overprovision_txq:
      decision = -(rounded_ewmm_txql - self.overprovision_txq)
      if rounded_ewma_u + decision > self.overprovision_cells: # check that we still have our overprovision in cells (compared to the avg.)
        self.ewmm_txql -= decision # mark our budget for the fact that we deallocated
      else:
        decision = 0 # no nothing

    return {
      "ewma_dq"  : self.ewma_dq,
      "ewma_u"   : self.ewma_u,
      "ewmm_u"   : real_ewmm_u,
      "ewmm_txql": real_ewmm_txql,
      "decision" : decision
    }

  def schema(self):
    return ["ewma_dq", "ewma_u", "ewmm_u", "ewmm_txql", "decision"]
