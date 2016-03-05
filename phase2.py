#!/usr/bin/python2.7

import sys

from random import *
from Queue import *
from bisect import *
from math import *

ARRIVAL = 0
TRANSMISSION = 1

MAX_PACKETS = 0
ARRIVAL_RATE = 0
NUM_HOSTS = 0

SYMBOL_RATE = 100000000
PROP_DELAY = 0.00001

currentIndex = -1 # position of current event to be examined
packetCount = -1 # count of packets sent; used to limit simulation

Hosts = []

def exp_dist(rate):
    """
    Exponential Distribution
    """ 
    u = random()
    return ((-1/rate) * log(1-u))

class Statistics:
    """
    Statistics outputs
    """
    
    def __init__(self, delay_count = 0, sent = 0):
        self.delay_count = delay_count
        self.sent = sent


# statistics
statistics = Statistics()

class Event:
    """
    Event class
    """

    def __init__(self, timei = 0, eventType = 0, source = None, packet = None, msg = "NULL"):
        self.time = time
        self.eventType = eventType
        self.source = source
        self.packet = packet
        self.msg = msg 

    def __lt__(self, other):
        return self.time < other.time

    def __repr__(self):
        return "<time = %d, eventType = %d, msg = %s>" % (self.time, self.eventType, self.msg)

    def __str__(self):
        return "<time = %d, eventType = %d, msg = %s>" % (self.time, self.eventType, self.msg)


class Packet:
    """
    Packet Class
    """

    def __init__(self, hops = 0, size = 0, arrival_time = 0):
        self.hops = hops
        self.size = size
        self.arrival_time = arrival_time


def arrival(eventList):
    """
    Process and Generate Arrival Events
    """ 
    currentEvent = eventList[currentIndex]
   
    # Generate next event with a new packet 
    nextTime = currentEvent.time + exp_dist(ARRIVAL_RATE) 

    global NUM_HOSTS
    nextp = Packet(hops = randint(0, NUM_HOSTS-1), size = randint(64, 1518), arrival_time = nextTime)

    insort(eventList, Event(time=nextTime, eventType=ARRIVAL, source = currentEvent.source ,packet = nextp))
    
    # enqueue packet of the current event
    global Hosts
    Hosts[currentEvent.packet.source].put(item = currentEvent.packet, block = False)


def transmission(eventList):
    """
    Process and Generate Transmission Events
    """
    currentEvent = eventList[currentIndex]
    Q = Hosts[currentEvent.source]
    TempQ = Q

    frameLength = 0
    global statistics 
    while not TempQ.empty():
        p = TempQ.get()
        frameLength += p.size

    global SYMBOL_RATE
    t_delay = frameLength/SYMBOL_RATE
    while not Q.empty():
        p = Q.get()
        global PROP_DELAY
        statistics.delay_count += (currentEvent.time - p.arrival_time) + p.hops * (t_delay + PROP_DELAY)
        statistics.sent += 1

    # Creates next transmission event
    nextTime = currentEvent.time + NUM_HOSTS * (t_delay + PROP_DELAY)
    
    insort(eventList, Event(time=nextTime, eventType=TRANSMISSION, source = (currentEvent.source+1)%NUM_HOSTS))


def main():
    # Argument Handling
    if(len(sys.argv) != 4):
        print("usage:", str(sys.argv[0]), "[lambda] [num hosts] [outfile]")
        return

    global MAX_PACKETS
    global ARRIVAL_RATE
    global NUM_HOSTS    

    ARRIVAL_RATE = float(sys.argv[1])
    NUM_HOSTS = int(sys.argv[2])
    outfile = str(sys.argv[3])

    print "ARRIVAL_RATE: %f" % ARRIVAL_RATE
    print "Number of hosts: %f" % NUM_HOSTS
    print "Writing output to file: %s" % outfile

    global Hosts
    for i in range(0,NUM_HOSTS):
        Hosts.append(Queue())


if __name__ == '__main__':
    main()
