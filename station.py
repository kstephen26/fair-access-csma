import random
import threading
import time
import queue


class Station(threading.Thread):
	'''
	Base class for implementing a wireless station (transmitter).
	'''

	def __init__(self, id, q_to_ap, q_to_station, pkts_p_sec, packet_size, packet_header, *args, **kwargs):
		self.id = id
		self.q_to_ap = q_to_ap
		self.q_to_station = q_to_station
		# print("packets per second: ", pkts_p_sec)
		self.interval = 1.0/pkts_p_sec
		self.last_tx = None
		self.packet_size = packet_size
		self.packet_header = packet_header
		print('Setting up station id:{}'.format(id))

		super().__init__(*args, **kwargs)

	def wait_for_next_transmission(self):
		'''
		Blocks until this station is ready to send another packet to the
		access point.
		'''

		# If we have already sent one packet
		if self.last_tx != None:
			# Check if we have waited long enough
			now = time.time()
			diff = now - self.last_tx
			if self.interval > diff:
				# Calculate how much more to wait, and add some randomness
				# while keeping the average interval the same

				to_wait = self.interval - diff
				# print(to_wait)
				to_wait += ((random.random() - 0.5) * (0.2*to_wait))
				final_wait = to_wait*self.packet_header['filesize']*(1/self.packet_header['latency'])*0.01
				# print("prev,now", to_wait, final_wait)
				# print('waiting... {}s'.format(to_wait))
				time.sleep(final_wait)

		self.last_tx = time.time()

	def receive(self):
		'''
		Blocks until a packet is received or a timeout expires.

		Valid return values are:
		- "ACK": The access point acknowledged our packet.
		- "CTS": The access point has granted us the wireless channel to
		         transmit a single data packet.
		- None:  No packet was received before the timeout.
		'''
		try:
			msg = self.q_to_station.get()
		except queue.Empty:
			return None
		if msg == 'ACK':
			return 'ACK'
		elif msg == 'NOACK':
			return None
		elif msg == 'NOCTS':
			return None

		return msg

	def send(self, pkt, pktheader):
		'''
		Send a packet to the access point. We change this function to send not only a packet but also a corresponding packet header.

		Valid packets are:
		- "DATA": A data packet.
		- "RTS":  A "Request to Send" packet.
		'''

		if pkt == 'RTS':
			self._send_to_access_point('RTS', pktheader, 'START')
			time.sleep(0.005) # 5 millisecond transmission time
			self._send_to_access_point('RTS', pktheader, 'DONE')

		elif pkt == 'DATA':
			self._send_to_access_point('DATA', pktheader, 'START')
			time.sleep(0.01) # 10 millisecond transmission time
			self._send_to_access_point('DATA', pktheader, 'DONE')

	def sense(self):
		'''
		Returns True if the wireless channel is occupied, false otherwise.
		'''
		pktheader = {}
		self._send_to_access_point('SENSE', pktheader)
		msg = self.q_to_station.get()
		if msg == 'channel_active':
			return True
		elif msg == 'channel_inactive':
			return False
		else:
			print('Huh?? Should not receive some other packet in sense.')
			print(msg)
			return None


	# Internal function, do not call from mac.py.
	def _send_to_access_point(self, type, header={}, modifier=''):
		to_send = {
			'id': self.id,
			'type': type,
			'mod': modifier,
			'header':header
		}
		self.q_to_ap.put(to_send)

