all: packetDelays.png throughput.png

results.csv: token_ring.py run.sh
	./run.sh

packetDelays.png: results.csv analysis.m
	octave-cli -i analysis.m

throughput.png: results.csv analysis.m
	octave-cli -i analysis.m
