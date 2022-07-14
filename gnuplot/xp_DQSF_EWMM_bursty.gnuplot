# Configure output mode and file
PREFIX="xp_DQSF_EWMM_bursty"
TARGET=-1
set xrange [0:1800]
set yrange [0:12]

load "__xp_DQSF_EWMx.inc.gnuplot"
unset key
load "__xp_DQSF_EWMM.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
