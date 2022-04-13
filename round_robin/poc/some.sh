#/usr/bin/env sh
set -x
rm some_res/*Switch.txt
./simu.py                 \
    --rr 3,5,7            \
    --count 1000          \
    --burst-range 10 20   \
    --trsmit-range 14 26  \
    --seed 72035          \
    --save-files 2> ./info.txt
mkdir some_res/
mv *Switch.txt some_res/

# with M burst max, if transmit range is M-n..M+n,
# should be sum(rr) >= 2*n
#       and rr_k > n for rr_k in rr
# (maybe, from observation with 8 queues and 3 vls,
# further testing would be needed)
