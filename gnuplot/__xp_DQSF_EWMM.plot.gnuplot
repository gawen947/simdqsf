# Actual plotting
plot DATA using 0:13 w lines lt ST_UNUSED    title 'cells unused', \
     DATA using 0:11 w lines lt ST_ALLOCATED title 'cells allocated', \
     TARGET title 'cells target' w lines lt ST_TARGET, \
     DATA using 0:14 w lines lt ST_DQ        title 'EWMA(ΔQ)', \
     DATA using 0:15 w lines lt ST_U         title 'EWMA(U)', \
     DATA using 0:16 w lines lt ST_EWMM_U    title 'WMM(U)',  \
     DATA using 0:17 w lines lt ST_TXQLEFT   title 'WMM(TxQ)'
