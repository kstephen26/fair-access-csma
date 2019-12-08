#!/usr/bin/env python3



import sys

import time

import threading

import queue

import access_point

import mac



# Handle command line arguments.

sys.argv = ['project.py', '4', '25', '100', 'neighbors', 'normal', 'RTS_CTS']



if len(sys.argv) != 7:

    print('Usage: {} <# stations> <pkts/s> <pkts> <tx range> <ap mode> <mac>'.format(sys.argv[0]))

    sys.exit(1)



NUMBER_STATIONS = int(sys.argv[1])

PACKETS_PER_SECOND = float(sys.argv[2])

PACKETS_TO_RECEIVE = int(sys.argv[3])

TX_RANGE = sys.argv[4]

AP_MODE = sys.argv[5]

MAC = sys.argv[6]



if TX_RANGE != 'all':

    TX_RANGE = 'neighbors'

if AP_MODE != 'special':

    AP_MODE = 'normal'

mac_protocol = mac.RTS_CTS

if MAC == 'NullMacExponentialBackoff':

    mac_protocol = mac.NullMacExponentialBackoff

elif MAC == 'CSMA_CA':

    mac_protocol = mac.CSMA_CA

elif MAC == 'RTS_CTS':

    mac_protocol = mac.RTS_CTS



print('Running Simulator. Settings:')

print('  Number of stations: {}'.format(NUMBER_STATIONS))

print('  Packets / second:   {}'.format(PACKETS_PER_SECOND))

print('  TX Range:           {}'.format(TX_RANGE))

print('  AP Mode:            {}'.format(AP_MODE))

print('  MAC Protocol:       {}'.format(mac_protocol))





# Track the start time of running the simulator.

start = time.time()



# Need a queue to simulate wireless transmissions to the access point.

q_to_ap = queue.Queue()

station_queues = []



# Setup and start each wireless station.

packet_headers = {0:{'latency':0.1, 'filetype':'video', 'filesize': 124}, 
                    1:{'latency':0.5, 'filetype':'music', 'filesize': 13},
                    2:{'latency':0.7, 'filetype':'text', 'filesize': 1},
                    3:{'latency':0.1, 'filetype':'music', 'filesize': 50}
                    }


for i in range(NUMBER_STATIONS):

    q = queue.Queue()

    station_queues.append(q)

    print(PACKETS_PER_SECOND)

    packet_size = i*100

    packet_header = packet_headers[i]

    t = mac_protocol(i, q_to_ap, q, PACKETS_PER_SECOND, packet_size, packet_header)

    t.daemon = True

    t.start()



    # Delay to space stations

    time.sleep((1.0/PACKETS_PER_SECOND) / NUMBER_STATIONS)



# And run the access point.

ap = access_point.AccessPoint(q_to_ap, station_queues, TX_RANGE, AP_MODE, PACKETS_TO_RECEIVE)

ap.run()



# When the access point stops running then we have received the correct number

# of packets from each station.

end = time.time()



print('Took {} seconds'.format(end-start), "\n")

sys.exit(0)

