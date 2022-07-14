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

MAX_TXQ   = 10
MAX_CELLS = 100
MIN_CELLS = 0

"""
Compute the Exponential Weighter Moving Maximum.
See ewmm_test for an example.
"""
def ewmm(e, x, alpha):
  if x >= e:
    return x
  else:
    return (1 - alpha) * e

"""
Here alpha represent a part of a unit.
That is the same unit as x.
"""
def ewmm2(e, x, alpha):
  if x >= e:
    return x
  else:
    return max(0, e - alpha)

def ewma(e, x, alpha):
  return x * alpha + (1 - alpha) * e

class SchedulingFunction(object):
  def schema(self):
    raise NotImplementedError
  def apply(self,
      iter_idx,  # Give some kind of SFrame Number
      sframe,    # The slotframe
      traffic,   # The traffic that was intended for this SFrame (not counting the drop)
      drop,      # Number of drop in this SFrame
      txq,       # Current size of TxQ
      old_txq):  # TxQ of the last SFrame
    raise NotImplementedError

class SixpRequest(object):
  sixp_request_id = 0

  def __init__(self, ttl, decision):
    self.ttl = ttl           # ttl until decision is done
    self.decision = decision # number of cells to alloc/dealloc
    self.id = SixpRequest.sixp_request_id
    SixpRequest.sixp_request_id += 1

  """
  If the request should be applied, updated the value of nb_cells_allocated accordingly.
  Also update the TTL.
  """
  def apply(self):
    if self.ttl == 0:
      self.ttl -= 1
      return self.decision
    self.ttl -= 1
    return 0

  """
  Return true if the request has expired (the decision was applied)
  and it should now be deleted.
  """
  def is_expired(self):
    return self.ttl < 0

  def __repr__(self):
    return "6P[%d,%d,%d]" % (self.id,self.ttl,self.decision)

class Slotframe(object):
  def __init__(self, sixp_delay):
    self.cells_allocated = MIN_CELLS
    self.cells_used      = 0
    self.sixp_delay      = sixp_delay
    self.sixp_requests   = []
    self.total_sixp      = 0

  # access by SF
  def get_cells_allocated(self):
    return self.cells_allocated
  def get_cells_used(self):
    return self.cells_used
  def get_cells_unused(self):
    return self.cells_allocated - self.cells_used

  """
  Allocation of deallocation (use negative number to deallocate).
  """
  def allocate(self, n):
    self.sixp_requests.append(SixpRequest(self.sixp_delay, n))
    self.total_sixp += 1

  # accessed by Simulation
  def slotframe_end(self):
    self.__apply_sixp_requests()
    self.cells_used = 0

  """
  We want to send n packets in this slotframe.
  Returns the number of packets left that were actually sent
  """
  def traffic(self, n):
    if n > self.cells_allocated:
      self.cells_used = self.cells_allocated
    else:
      self.cells_used = n
    return self.cells_used

  def pending_sixp_requests(self):
    return len(self.sixp_requests)

  def total_sixp_requests(self):
    return self.total_sixp

  """
  Effective allocation (the SixpRequest completed).
  """
  def __effective_allocation(self, n):
    self.cells_allocated += n
    if self.cells_allocated > MAX_CELLS:
      self.cells_allocated = MAX_CELLS
    if self.cells_allocated < MIN_CELLS:
      self.cells_allocated = MIN_CELLS

  def __apply_sixp_requests(self):
    for i, req in enumerate(self.sixp_requests):
      decision = req.apply()
      if decision != 0:
        self.__effective_allocation(decision)
      if req.is_expired():
        del self.sixp_requests[i]

class Simulation(object):
  def __init__(self, max_iter, sixp_delay, traffic_pattern, schedfun, print_results_fun):
    self.max_iter        = max_iter
    self.traffic_pattern = traffic_pattern
    self.schedfun        = schedfun
    self.sixp_delay      = sixp_delay
    self.sixp_requests   = []
    self.print_results   = print_results_fun

    self.print_results.start(schedfun)

  def __iter__(self):
    # current state of the SFrame
    self.iter_idx = 0
    self.txq      = 0
    self.old_txq  = 0 # SFun often need that
    self.sframe   = Slotframe(self.sixp_delay)

    # stuff for stats
    self.total_sixp         = 0
    self.total_drop         = 0
    self.total_traffic      = 0
    self.total_cells        = 0
    self.total_unused_cells = 0
    self.total_used_cells   = 0

    self.total_sixp_at3600            = 0
    self.total_sixp_after3600         = 0
    self.total_drop_after3600         = 0
    self.total_traffic_after3600      = 0
    self.total_cells_after3600        = 0
    self.total_unused_cells_after3600 = 0
    self.total_used_cells_after3600   = 0


    return self # IMA iterator

  def __next__(self):
    if self.max_iter is not None and self.max_iter > 0 and self.iter_idx > self.max_iter:
      self.total_sixp = self.sframe.total_sixp_requests()
      self.total_sixp_after3600 = self.total_sixp - self.total_sixp_at3600
      self.print_results.end(self)
      raise StopIteration

    # reset everything
    self.sframe.slotframe_end()
    self.old_txq = self.txq
    drop         = 0

    # traffic that arrive at this slotframe
    traffic = self.traffic_pattern[self.iter_idx % len(self.traffic_pattern)]
    self.total_traffic           += traffic
    self.total_traffic_after3600 += traffic if self.iter_idx > 3600 else 0

    # impact of this traffic on the TxQ and drop
    self.txq += traffic
    if self.txq > MAX_TXQ:
      drop     = self.txq - MAX_TXQ
      self.txq = MAX_TXQ
      # stats
      self.total_drop           += drop
      self.total_drop_after3600 += drop if self.iter_idx > 3600 else 0

    # how much of the traffic could we send in this SFrame
    self.txq -= self.sframe.traffic(self.txq)

    res = self.schedfun.apply(
      self.iter_idx, # Give some kind of SFrame Number
      self.sframe,   # The slotframe
      traffic,       # The traffic that was intended for this SFrame (not counting the drop)
      drop,          # Number of drop in this SFrame
      self.txq,      # Current size of TxQ
      self.old_txq   # TxQ of the last SFrame
    )


    decision = res["decision"]
    if decision != 0:
      self.sframe.allocate(decision)

    # for now results only contains the scheduling function metrics
    # along with its final decision
    # we add the simulation metrics here
    avgtraf             = float(self.total_traffic) / (self.iter_idx + 1)
    errtraf             = avgtraf - self.sframe.get_cells_allocated()
    res["iter"]         = self.iter_idx
    res["traffic"]      = traffic
    res["tottraf"]      = self.total_traffic
    res["totdrop"]      = self.total_drop
    res["totsixp"]      = self.sframe.total_sixp_requests()
    res["avgtraf"]      = avgtraf
    res["errtraf"]      = errtraf
    res["drop"]         = drop
    res["txq_old"]      = self.old_txq
    res["txq_new"]      = self.txq
    res["cells"]        = self.sframe.get_cells_allocated()
    res["cells_used"]   = self.sframe.get_cells_used()
    res["cells_unused"] = self.sframe.get_cells_unused()
    res["sixp"]         = self.sframe.pending_sixp_requests()

    self.total_cells        += self.sframe.get_cells_allocated()
    self.total_unused_cells += self.sframe.get_cells_unused()
    self.total_used_cells   += self.sframe.get_cells_used()
    if self.iter_idx > 3600:
      self.total_cells_after3600        += self.sframe.get_cells_allocated()
      self.total_unused_cells_after3600 += self.sframe.get_cells_unused()
      self.total_used_cells_after3600   += self.sframe.get_cells_used()
    elif self.iter_idx == 3600:
      self.total_sixp_at3600 = self.sframe.total_sixp_requests()

    self.print_results.print(self.schedfun, res)
    self.iter_idx += 1
    return res

class PrintMethod(object):
  DEFAULT_SIM_ORDER = [
    "iter",
    "traffic",
    "avgtraf",
    "errtraf",
    "tottraf",
    "totsixp",
    "totdrop",
    "drop",
    "txq_old",
    "txq_new",
    "cells",
    "cells_used",
    "cells_unused" ]

  @staticmethod
  def start(schedfun):
    raise NotImplementedError

  @staticmethod
  def print(schedfun, res):
    raise NotImplementedError

  @staticmethod
  def end(schedfun):
    raise NotImplementedError

  @staticmethod
  def _pct_traffic(sim, value):
    return ((100. * value) / sim.total_traffic)

  @staticmethod
  def _pct_cells(sim, value):
    return ((100. * value) / sim.total_cells)

  @staticmethod
  def _pct_traffic_after3600(sim, value):
    return ((100. * value) / sim.total_traffic_after3600)

  @staticmethod
  def _pct_cells_after3600(sim, value):
    return ((100. * value) / sim.total_cells_after3600)

class PrintNull(PrintMethod):
  @staticmethod
  def start(schedfun):
    pass

  @staticmethod
  def print(schedfun, res):
    pass

  @staticmethod
  def end(sim):
    pass

class PrintDefault(PrintMethod):
  @staticmethod
  def start(schedfun):
    pass

  @staticmethod
  def print(schedfun, res):
    print(res)

  @staticmethod
  def end(sim):
    pass


class PrintHuman(PrintMethod):
  @staticmethod
  def start(schedfun):
    pass

  @staticmethod
  def _print_field_as_human(name, value, format):
    print(("%s="+format) % (name, value),end=' ')
  @staticmethod
  def print_field_as_human(res, name):
    value = res[name]

    if type(value) == type(1.0):
      PrintHuman._print_field_as_human(name, value, "% +3.3f")
    elif type(value) == type(1):
      PrintHuman._print_field_as_human(name, value, "% +3d")
    else:
      PrintHuman._print_field_as_human(name, value, "%s")
  @staticmethod
  def print_field_as_human_and_delete(res, name):
    PrintHuman.print_field_as_human(res, name)
    del res[name]

  @staticmethod
  def print(schedfun, res):
    for k in PrintMethod.DEFAULT_SIM_ORDER:
      PrintHuman.print_field_as_human_and_delete(res, k)
    for k in res.keys():
      PrintHuman.print_field_as_human(res, k)

    print('')

  @staticmethod
  def end(sim):
    pass


class PrintPlot(PrintMethod):
  @staticmethod
  def start(schedfun):
    print("#",end=' ')
    for k in PrintMethod.DEFAULT_SIM_ORDER:
      print(k,end=' ')
    for k in schedfun.schema():
      print(k,end=' ')
    print('')

  @staticmethod
  def print(schedfun, res):
    schema = PrintMethod.DEFAULT_SIM_ORDER + schedfun.schema()
    for k in schema:
      print(res[k], end=' ')
    print('')

  @staticmethod
  def end(sim):
    print("#")
    print("# Final report:")
    print("#   total_traffic     :", sim.total_traffic)
    print("#   total_sixp        :", sim.total_sixp)
    print("#   total_drop        :", sim.total_drop)
    print("#   total_cells       :", sim.total_cells)
    print("#   total_unused_cells:", sim.total_unused_cells)
    print("#   total_used_cells  :", sim.total_used_cells)
    print("#")
    print("#   pct_sixp          :", PrintMethod._pct_traffic(sim, sim.total_sixp))
    print("#   pct_drop          :", PrintMethod._pct_traffic(sim, sim.total_drop))
    print("#   pct_unused_cells  :", PrintMethod._pct_cells(sim, sim.total_unused_cells))
    print("#   pct_used_cells    :", PrintMethod._pct_cells(sim, sim.total_used_cells))
    print("#")
    print("#")
    print("#")
    print("# After t=3600:")
    print("#   total_traffic     :", sim.total_traffic_after3600)
    print("#   total_sixp        :", sim.total_sixp_after3600)
    print("#   total_drop        :", sim.total_drop_after3600)
    print("#   total_cells       :", sim.total_cells_after3600)
    print("#   total_unused_cells:", sim.total_unused_cells_after3600)
    print("#   total_used_cells  :", sim.total_used_cells_after3600)
    print("#")
    print("#   pct_sixp          :", PrintMethod._pct_traffic_after3600(sim, sim.total_sixp_after3600))
    print("#   pct_drop          :", PrintMethod._pct_traffic_after3600(sim, sim.total_drop_after3600))
    print("#   pct_unused_cells  :", PrintMethod._pct_cells_after3600(sim, sim.total_unused_cells_after3600))
    print("#   pct_used_cells    :", PrintMethod._pct_cells_after3600(sim, sim.total_used_cells_after3600))

