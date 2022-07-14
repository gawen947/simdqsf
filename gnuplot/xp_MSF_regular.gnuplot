# Configure output mode and file
PREFIX="xp_MSF_regular"
TARGET=7
set xrange [0:1800]
set yrange [0:15]

load "__xp_DQSF_EWMx.inc.gnuplot"
#unset key
load "__xp_MSF.plot.gnuplot"
load "__xp_MSF.post.gnuplot"
