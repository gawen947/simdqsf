# common configuration for the DQSF EWMA and EWMM plots
set term eps enhanced color size 10cm, 5cm
set key box opaque top right
set grid

PREFIX="xp_DQSF_EWMM_random_a"
set output PREFIX.".eps"
DATA=PREFIX.".data"

set grid

set ylabel  "Tot. 6P / Tot. drops"
set y2label "Tot. cells used (%)"
set y2tics 20
set xlabel "α"

set xrange [0:1]
set yrange [0:50]
set y2range [0:100]

# Define color and linestyle for each metric.
COLOR_BLUE="#0273bd"
COLOR_ORANGE="#d9551c"
COLOR_GREEN="#77ac30"
COLOR_YELLOW="#edb122"
COLOR_PURPLE="#7f318f"
COLOR_CYAN="#4ebeee"
COLOR_RED="#a00f2a"
COLOR_BLACK="#000000"

set label "▼ lower is better" at screen 0.12422, 0.97
set label "higher is better ▲" at screen 0.565, 0.97

plot DATA using 1:3  axes x1y1 lc rgb COLOR_YELLOW pt 7 ps 0.3 title "Total 6P", \
     DATA using 1:4  axes x1y1 lc rgb COLOR_RED    pt 6 ps 0.3 title "Total drops", \
     DATA using 1:12 axes x1y2 lc rgb COLOR_GREEN  pt 4 ps 0.3 title "Total cells used"