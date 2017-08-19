set terminal postscript eps enhanced color font 'Helvetica, 80'
set output 'static.eps'
set size 6, 4
set xlabel 'Tiempo'
set ylabel 'Frames por segundo'
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
plot "static.dat" using 1 with lines lw 20 linetype 10 linecolor rgb "#a1a1a1" title 'Ambiente estatico';

set terminal postscript eps enhanced color font 'Helvetica, 80'
set output 'movement.eps'
set size 6, 4
set xlabel 'Tiempo'
set ylabel 'Frames por segundo'
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
plot "movement.dat" using 1 with lines lw 20 linetype 10 linecolor rgb "#a1a1a1" title 'Ambiente con movimiento';

set terminal postscript eps enhanced color font 'Helvetica, 80'
set output 'scaning.eps'
set size 6, 4
set xlabel 'Tiempo'
set ylabel 'Frames por segundo'
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
plot "scaning.dat" using 1 with lines lw 20 linetype 10 linecolor rgb "#a1a1a1" title 'Escaneando QR code';

set terminal postscript eps enhanced color font 'Helvetica, 60'
set output 'all.eps'
set size 6, 4
set xlabel 'Tiempo'
set ylabel 'Frames por segundo'
set grid ytics lt 0 lw 1 lc rgb "#bbbbbb"
set grid xtics lt 0 lw 1 lc rgb "#bbbbbb"
plot "scaning.dat" using 1 with points lw 30 pt 8 lc rgb "#00e100" title 'Escaneando QR code', \
"movement.dat" using 1 with points lw 30 pt 16 lc rgb "#0000e1" title 'Ambiente con movimiento', \
"static.dat" using 1 with points lw 30 pt 17 lc rgb "#e10000" title 'Ambiente estatico';
