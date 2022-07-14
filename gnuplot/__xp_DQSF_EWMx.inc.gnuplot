# common configuration for the DQSF EWMA and EWMM plots
set term eps enhanced color size 10cm, 5cm
set key box opaque top right
set grid

set output PREFIX.".eps"
DATA=PREFIX.".data"

set ylabel "Metric value"
set xlabel "Number of slotframes"

#set xrange [0:300]
#set yrange [0:30]


# Define color and linestyle for each metric.
COLOR_BLUE="#0273bd"
COLOR_ORANGE="#d9551c"
COLOR_GREEN="#77ac30"
COLOR_YELLOW="#edb122"
COLOR_PURPLE="#7f318f"
COLOR_CYAN="#4ebeee"
COLOR_RED="#a00f2a"
COLOR_BLACK="#000000"

ST_DQ=1
ST_U=2
ST_EWMM_U=3
ST_TXQLEFT=4
ST_UNUSED=5
ST_ALLOCATED=6
ST_TARGET=7
ST_LINE=8

METRIC_LINEWIDTH=1.5
TARGET_LINEWIDTH=2

# Define linestyles
set linetype ST_DQ        lc rgb COLOR_BLUE   lw METRIC_LINEWIDTH
set linetype ST_U         lc rgb COLOR_YELLOW lw METRIC_LINEWIDTH
set linetype ST_EWMM_U    lc rgb COLOR_PURPLE lw METRIC_LINEWIDTH
set linetype ST_TXQLEFT   lc rgb COLOR_CYAN   lw METRIC_LINEWIDTH
set linetype ST_UNUSED    lc rgb COLOR_GREEN  lw METRIC_LINEWIDTH
set linetype ST_ALLOCATED lc rgb COLOR_RED    lw METRIC_LINEWIDTH
set linetype ST_TARGET    lc rgb COLOR_BLACK  lw TARGET_LINEWIDTH
set linetype ST_LINE      lc rgb COLOR_BLACK  lw TARGET_LINEWIDTH dashtype 2
