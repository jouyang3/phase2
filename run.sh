#!/bin/bash

hostNums="10 25"
lambdas="0.01 0.05 0.1 0.2 0.3 0.5 0.6 0.7 0.8 0.9"
pids=""
outfile=results.csv

rm -f $outfile

for hostNum in $hostNums; do
	for lambda in $lambdas; do
		./token_ring.py $lambda $hostNum >> $outfile &
		pids="$pids $!"
		echo Starting $!: $lambda, $hostNum
	done
done


for pid in $pids; do
	wait
done

sort -t, -k2,2n -k1,1n $outfile -o $outfile
