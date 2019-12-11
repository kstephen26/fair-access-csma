#!/usr/bin/env python3



import sys

import time

import threading

import queue

import access_point

import mac

count = 0

# Handle command line arguments.
# for i in range(3):
sys.argv = ['project.py', '4', '25', '10', 'neighbors', 'normal', 'RTS_CTS']



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

packet_headers = {0:{'latency':0.1, 'filetype':'video', 'filesize': 1200}, 
                    1:{'latency':0.5, 'filetype':'music', 'filesize': 10},
                    2:{'latency':0.7, 'filetype':'text', 'filesize': 5},
                    3:{'latency':0.1, 'filetype':'music', 'filesize': 50},
                    4:{'latency':0.1, 'filetype':'video', 'filesize': 1200}, 
                    5:{'latency':0.5, 'filetype':'music', 'filesize': 10},
                    6:{'latency':0.7, 'filetype':'text', 'filesize': 5},
                    7:{'latency':0.1, 'filetype':'music', 'filesize': 50},
                    8:{'latency':0.1, 'filetype':'video', 'filesize': 1200}, 
                    9:{'latency':0.5, 'filetype':'music', 'filesize': 10},
                    10:{'latency':0.7, 'filetype':'text', 'filesize': 6},
                    11:{'latency':0.1, 'filetype':'music', 'filesize': 80},
                    12:{'latency':0.1, 'filetype':'video', 'filesize': 1230}, 
                    13:{'latency':0.5, 'filetype':'music', 'filesize': 14},
                    14:{'latency':0.7, 'filetype':'text', 'filesize': 1},
                    15:{'latency':0.1, 'filetype':'music', 'filesize': 50}
                    }

costs = []
avgSize = 0
avgLatency = 0

for i in range(NUMBER_STATIONS):
    avgSize += i*packet_headers[i]['filesize']
    avgLatency += packet_headers[i]['latency']

avgSize = avgSize / NUMBER_STATIONS
avgLatency = avgLatency / NUMBER_STATIONS

for i in range(NUMBER_STATIONS):

    q = queue.Queue()
    station_queues.append(q)

    print(PACKETS_PER_SECOND)

    packet_size = i*packet_headers[i]['filesize']

    packet_header = packet_headers[i]

    if packet_header['filetype'] == 'music':
        filecost = 0.9 
    elif packet_header['filetype'] == 'video':
        filecost = 0.8
    elif packet_header['filetype'] == 'text':
        filecost = 0.3
    costs.append(0.01*packet_header['filesize']*filecost/packet_header['latency'])

    t = mac_protocol(i, q_to_ap, q, PACKETS_PER_SECOND, packet_size, packet_header)

    t.daemon = True

    t.start()


        # Delay to space stations

    time.sleep((1.0/PACKETS_PER_SECOND) / NUMBER_STATIONS)



# And run the access point.

ap = access_point.AccessPoint(q_to_ap, station_queues, TX_RANGE, costs, avgLatency, avgSize, AP_MODE, PACKETS_TO_RECEIVE, )

ap.run()



# When the access point stops running then we have received the correct number

# of packets from each station.

end = time.time()


count += end - start

print('Took {} seconds'.format(end-start), "\n")
# print(count/3)
sys.exit(0)

