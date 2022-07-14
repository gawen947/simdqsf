# Configure output mode and file
PREFIX="xp_DQSF_EWMA_regular_a=0.1"
TARGET=7
set xrange [0:50]
set yrange [0:30]

load "__xp_DQSF_EWMx.inc.gnuplot"
unset key
load "__xp_DQSF_EWMA.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
