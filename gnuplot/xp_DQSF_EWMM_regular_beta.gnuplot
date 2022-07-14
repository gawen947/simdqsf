# Configure output mode and file
PREFIX="xp_DQSF_EWMM_regular_beta"
TARGET=7
set xrange [0:200]
set yrange [0:30]

load "__xp_DQSF_EWMx.inc.gnuplot"
unset key
load "__xp_DQSF_EWMM.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
