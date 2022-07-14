# Configure output mode and file
PREFIX="xp_DQSF_EWMM_random"
TARGET=4
set xrange [0:3600]
set yrange [0:25]

load "__xp_DQSF_EWMx.inc.gnuplot"
unset key
load "__xp_DQSF_EWMM.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
