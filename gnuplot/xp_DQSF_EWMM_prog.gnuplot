# Configure output mode and file
PREFIX="xp_DQSF_EWMM_prog"
#TARGET=7
LINE(x)= x < 3600 ? 2 : x > 4320 ? 8 : 2+((x-3600)/120)
LINE_TITLE="Traffic (pkts/sf)"
set xrange [3400:4500]
set yrange [0:12]

load "__xp_DQSF_EWMx.inc.gnuplot"
set term eps enhanced color size 10cm, 7cm
set key above
set key noopaque
#set key center top

ALLOC_SYMBOL_HEIGHT=11
ALLOC_SYMBOL="▼"
set label ALLOC_SYMBOL at first 3736,ALLOC_SYMBOL_HEIGHT center
set label ALLOC_SYMBOL at first 3857,ALLOC_SYMBOL_HEIGHT center
set label ALLOC_SYMBOL at first 3977,ALLOC_SYMBOL_HEIGHT center
set label ALLOC_SYMBOL at first 4097,ALLOC_SYMBOL_HEIGHT center
set label ALLOC_SYMBOL at first 4219,ALLOC_SYMBOL_HEIGHT center

set label "Allocation  ▼" at screen 0.7, 0.8175

load "__xp_DQSF_EWMM_line.plot.gnuplot"
load "__xp_DQSF_EWMx.post.gnuplot"
