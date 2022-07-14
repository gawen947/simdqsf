# Actual plotting
plot DATA using 0:13 w lines lt ST_UNUSED    title 'cells unused', \
     DATA using 0:11 w lines lt ST_ALLOCATED title 'cells allocated', \
     DATA using 0:14 w lines lt ST_DQ        title 'EWMA(ΔQ)', \
     DATA using 0:15 w lines lt ST_U         title 'EWMA(U)'
#     TARGET title 'cells target' w lines lt ST_TARGET
