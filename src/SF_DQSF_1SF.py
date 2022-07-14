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

# Does not do any averaging.
# Just uses one slotframe to compute \DeltaQ and U
# Of course it's really bad. It never stop allocating and deallocating.

class SchedulingFunction(sim.SchedulingFunction):
  def __init__(self, alpha, overprovision):
    # params
    self.alpha = alpha
    self.overprovision = overprovision

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame
    dq = txq - old_txq
    u  = sframe.get_cells_unused()

    if drop > 0:
      dq += drop # immediately allocate cells

    decision = 0
    if dq > 0:
      decision = dq
    elif u > self.overprovision:
      decision = -(u - self.overprovision)

    return {
      "decision": decision
    }

  def schema(self):
    return ["decision"]