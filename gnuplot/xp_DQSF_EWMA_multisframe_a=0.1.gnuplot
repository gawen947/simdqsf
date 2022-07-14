# Configure output mode and file
PREFIX="xp_DQSF_EWMA_multisframe_a=0.1"
TARGET=4
set xrange [0:50]
set yrange [0:14]

load "__xp_DQSF_EWMx.inc.gnuplot"
load "__xp_DQSF_EWMA.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
