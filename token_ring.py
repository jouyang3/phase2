#!/bin/python3.5

import sys
from math import *
from random import *
from bisect import insort
from queue import *

#PRINTOUTS = False


# Constants
MAX_TRANSMISSIONS = 1E6
PACKET_SIZE_LOWER_BOUND = 64
PACKET_SIZE_UPPER_BOUND = 1518
SYMBOL_RATE = 100E6
PROP_DELAY= 10E-6



class Statistics(object):
	def __init__(self):
		self.delayCount = 0
		self.bitsSent = 0  
		self.packetsSent = 0
		self.transmissions = 0

	def print_results(self, duration, network):
		throughput = self.bitsSent / duration
		avgPacketDelay = self.delayCount / self.packetsSent
		print("{},{},{},{}".format(
			network.arrivalRate,
			network.numHosts,
			throughput,
			avgPacketDelay))



class Behavior(object):
	def __init__(self, maxTransmissions, arrivalRate, numHosts, symbolRate, propDelay):
		self.maxTransmissions= maxTransmissions # maximum transmissionsto simulate
		self.arrivalRate = arrivalRate # lambda, parameter for Poisson distribution
		self.numHosts = numHosts # number of hosts in toten ring
		self.symbolRate = symbolRate # transmission rate (bits per second)
		self.propDelay = propDelay # propagation delay. (seconds)



class Packet(object):
	def __init__(self, arrivalTime, numHosts):
		self.arrivalTime = arrivalTime
		self.hops = randint(0, numHosts-1) # links from source to destination
		self.size = randint(PACKET_SIZE_LOWER_BOUND, PACKET_SIZE_UPPER_BOUND)



class Host(object):
	def __init__(self):
		self.nextHost = None
		self.queue = []
		self.frameLength = 0



class Event(object):
	def __init__(self, time, host):
		self.time = time
		self.host = host

	def __lt__(self, other):
		return self.time < other.time



class Arrival(Event):
	def __init__(self, time, host, packet):
		self.time = time
		self.host = host
		self.packet = packet

	def process(self, network, eventList, hosts, stats):
		# enqueue packet of the current event
		self.host.queue.append(self.packet)
		self.host.frameLength += self.packet.size # precompute frame length

		# Generate next Arrival with a new packet 
		nextTime = self.time + exp_dist(network.arrivalRate) 
		nextPacket = Packet(arrivalTime = nextTime, numHosts = len(hosts))

		nextEvent = Arrival(
			time = nextTime,
			host = self.host,
			packet = nextPacket)

		eventList.put(nextEvent)

		"""
		print("A ", self.packet.size,
			" bit packet arrived at host", hosts.index(self.host))
		"""



class Transmission(Event):
	def __init__(self, time, host):
		self.time = time
		self.host = host

	def process(self, network, eventList, hosts, stats):
		stats.transmissions += 1	

		# Generate next transmission
		transDelay = self.host.frameLength / network.symbolRate
		nextTime = self.time + (len(hosts) * (transDelay + network.propDelay))

		nextEvent = Transmission(time = nextTime, host = self.host.nextHost)

		eventList.put(nextEvent)

		# Compute statistics
		stats.bitsSent += self.host.frameLength

		for packet in self.host.queue:
			queueDelay = self.time - packet.arrivalTime
			linkDelay = transDelay + network.propDelay

			stats.delayCount += queueDelay + (packet.hops * linkDelay)
			stats.packetsSent += 1

		"""
		print("Transmitting ", self.host.frameLength,
			" bit frame at host", hosts.index(self.host),
			". Next host: ", hosts.index(self.host.nextHost))
		"""

		# Dequeue all packets added to frame
		self.host.queue.clear()
		self.host.frameLength = 0




def exp_dist(rate):
	u = uniform(0, 1) # uniform random variable
	timeInterval = (-1.0/rate) * log(1-u) # Poisson time interval
	return timeInterval



def main():
	if len(sys.argv) != 3:
		print("usage:", str(sys.argv[0]), "[arrival rate] [number of hosts]")
		return -1

	network = Behavior(
		maxTransmissions= MAX_TRANSMISSIONS,
		arrivalRate = float(sys.argv[1]),
		numHosts = int(sys.argv[2]),
		symbolRate = SYMBOL_RATE,
		propDelay = PROP_DELAY)

	stats = Statistics() # simulation statistics

	eventList = PriorityQueue() # simulation event list
	hosts = [] # list of hosts on network

	# For each host, create an empty queue and insert a new arrival
	for hostIndex in range(network.numHosts):
		hosts.append(Host())
		
		# Insert initial event
		nextTime = 0
		nextPacket = Packet(arrivalTime = nextTime, numHosts = len(hosts))

		nextEvent = Arrival(
			time = nextTime,
			host = hosts[-1], # The host most recently appended
			packet = nextPacket)

		eventList.put(nextEvent)

	# Create a circular ring of hosts
	for hostIndex in range(network.numHosts - 1):
		hosts[hostIndex].nextHost = hosts[hostIndex + 1]
	
	hosts[-1].nextHost = hosts[0]; # last host points to first

	# Schedule first token to arbitrary host (first host)
	nextEvent = Transmission(time = 0, host = hosts[0])
	eventList.put(nextEvent)

	# Start simulation
	thisEvent = None
	while stats.transmissions < network.maxTransmissions:
		thisEvent = eventList.get()
		thisEvent.process(network, eventList, hosts, stats)
		"""
		if PRINTOUTS is True:
			sys.stdout.write("\rPackets Sent = {:<7}, Transmissions = {:<14}, Time = {:<25}".format(
				stats.packetsSent, stats.transmissions, thisEvent.time))
			sys.stdout.flush()
		"""
		
	"""
	if PRINTOUTS is True:
		print("")
	"""

	# Compute final statistics and print
	stats.print_results(thisEvent.time, network)

	return 0
	

if __name__ == '__main__':	
	main()
