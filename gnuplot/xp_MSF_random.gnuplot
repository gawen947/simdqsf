# Configure output mode and file
PREFIX="xp_MSF_random"
TARGET=4
set xrange [0:3600]
set yrange [0:10]

load "__xp_DQSF_EWMx.inc.gnuplot"
unset key
load "__xp_MSF.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
