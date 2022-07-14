# Actual plotting
plot DATA using 1:13 w lines lt ST_UNUSED    title 'cells unused', \
     DATA using 1:11 w lines lt ST_ALLOCATED title 'cells allocated', \
     TARGET title 'cells target' w lines lt ST_TARGET
#     DATA using 1:($14*100) w lines lt ST_DQ        title 'MSF TX'
