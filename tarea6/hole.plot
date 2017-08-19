set terminal postscript eps enhanced color font 'Helvetica,40'
set output 'histogram.eps'
set size 4, 4
set xlabel 'pixel line'
set ylabel 'sum of intensities'
plot "vertical.dat" using 1:2 with lines lw 10 title 'vertical histogram',\
"horizontal.dat" using 1:2 with lines lw 10 title 'horizontal histogram'