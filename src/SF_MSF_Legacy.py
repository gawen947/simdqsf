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

# We reimplement MSF legacy here.
# Note that we cheat a bit since we decide on each slotframe and
# not exactly at the end of MAX_NUMCELLS

class SchedulingFunction(sim.SchedulingFunction):
  def __init__(self, low, high, max_numcells):
    # params
    self.low = low
    self.high = high
    self.max_numcells = max_numcells

    self.elapsed = 0
    self.used    = 0

  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame

    # ensure that we have at least one cell allocated
    if sframe.get_cells_allocated() == 0:
      return {
        "usage" : 0.0,
        "decision" : 1
      }

    self.elapsed += sframe.get_cells_allocated()
    self.used    += sframe.get_cells_used()
    usage    = 0.0
    decision = 0

    if self.elapsed > self.max_numcells:
      usage = float(self.used) / self.elapsed

      if usage > self.high:
        decision = 1
      if usage < self.low:
        decision = -1

      # we cheat a bit here
      self.elapsed = max(0, self.elapsed - self.max_numcells)
      self.used    = max(0, self.used - usage * self.max_numcells)

    return {
      "usage"   : usage,
      "decision": decision
    }

  def schema(self):
    return ["usage", "decision"]