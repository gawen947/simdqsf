# Configure output mode and file
PREFIX="xp_DQSF_EWMA_bursty_a=0.1"
set xrange [0:300]
set yrange [0:14]

load "__xp_DQSF_EWMx.inc.gnuplot"
load "__xp_DQSF_EWMA_notarget.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
