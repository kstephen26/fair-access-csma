

class AccessPoint():
	'''
	Main controller of the network that collects packets from each station.
	'''

	def __init__(self, recv_queue, station_queues, tx_range, ap_mode='normal', pkts_to_receive=100):
		# Save the queues we use to talk to the stations.
		self.recv_queue = recv_queue
		self.station_queues = station_queues

		# Save configuration about how the network should work.
		self.tx_range = tx_range
		self.ap_mode = ap_mode
		self.pkts_to_receive = pkts_to_receive

		# Keep track of what each station is doing, how many packets we
		# have received from each station, and, if needed, which station has
		# control of the wireless channel.
		self.active = []
		for i in range(len(station_queues)):
			self.active.append({'tx': None, 'corrupted': False})
		self.pkts_received = [0]*len(station_queues)
		self.cts_node = None


	def run(self):
		# Loop until we have enough packets from each station.
		while True:
			# Wait until we have a "packet" to receive from some station.
			# Note: packets are actually two queue messages: a START and a DONE
			# message.
			msg = self.recv_queue.get()

			# print('AP: {} sent {}({})'.format(msg['id'], msg['type'], msg['mod']))

			# Handle each message appropriately.
			if msg['type'] == 'SENSE':
				# Determine if the wireless channel is reserved.
				if self.cts_node != None:
					self._send_to_station(msg['id'], 'channel_active')
				else:
					# Determine if the node should be able to hear messages
					# from other nodes.
					active = self._check_for_tx(msg['id'])
					if active:
						self._send_to_station(msg['id'], 'channel_active')
					else:
						self._send_to_station(msg['id'], 'channel_inactive')

			elif msg['type'] == 'DATA':
				# Check that the stations are playing by the rules.
				if self.cts_node != None and self.cts_node != msg['id']:
					print('AP ERROR! A station without CTS sent data!')
					break

				if msg['mod'] == 'START':
					# Mark that this node is transmitting
					self.active[msg['id']]['tx'] = 'DATA'
					# Check if any other transmissions should be corrupted
					self._check_for_collisions(msg['id'])

				elif msg['mod'] == 'DONE':
					# for i,station in enumerate(self.active):
					# 	print('{}: t:{} c:{};  '.format(i, station['tx'], station['corrupted']), end='')
					# print('')

					# Ok the packet is done being sent. If it isn't corrupted
					# we count it and send ACK
					if self.active[msg['id']]['corrupted'] == False:
						self.pkts_received[msg['id']] += 1
						self.active[msg['id']]['tx'] = None
						self.cts_node = None
						self._send_to_station(msg['id'], 'ACK')
						#print('AP: Got packet #{} from station id:{}'.format(self.pkts_received[msg['id']], msg['id']))
					else:
						# Packet was corrupted, nothing we can do.
						self.active[msg['id']]['tx'] = None
						self.active[msg['id']]['corrupted'] = False
						self._send_to_station(msg['id'], 'NOACK')

						# print('AP: Data packet from {} was corrupted'.format(msg['id']))

			elif msg['type'] == 'RTS':
				if msg['mod'] == 'START':
					self.active[msg['id']]['tx'] = 'RTS'
					# Check if any other transmissions should be corrupted
					self._check_for_collisions(msg['id'])


				elif msg['mod'] == 'DONE':
					if self.active[msg['id']]['corrupted'] == False:
						if self.cts_node != None:
							print('Um, another node has control!')
						else:
							self.cts_node = msg['id']
							self._send_to_station(msg['id'], 'CTS')

					else:
						# Packet was corrupted, nothing we can do.
						self.active[msg['id']]['tx'] = None
						self.active[msg['id']]['corrupted'] = False
						self._send_to_station(msg['id'], 'NOCTS')



			# Check if we are all done (we have received enough packets from
			# each node).
			received_all = True
			for station_pkt_count in self.pkts_received:
				if station_pkt_count < self.pkts_to_receive:
					received_all = False
					break
			if received_all:
				print(self.pkts_received)
				break


	##
	## Internal Functions
	##

	def _check_for_collisions(self, id):
		# If there are no collisions at the access point then we can
		# quickly return.
		if self.ap_mode == 'special':
			return False

		# Check if any other transmissions should be corrupted
		corrupted = False
		for i,node in enumerate(self.active):
			if i == id:
				continue
			if node['tx'] != None:
				corrupted = True
				node['corrupted'] = True
		# If any other node was also transmitting we need to
		# mark the newly sending node as corrupted too
		if corrupted:
			self.active[id]['corrupted'] = True

	def _send_to_station(self, id, msg):
		self.station_queues[id].put(msg)

	def _send_to_other_stations(self, id, msg):
		for i,node in enumerate(self.active):
			if i == id:
				continue
			else:
				self._send_to_station(i, msg)

	def _check_for_tx(self, id):
		if self.tx_range == 'all':
			for node in self.active:
				if node['tx'] != None:
					return True
			return False
		elif self.tx_range == 'none':
			return False
		else:
			neighbors = [(id-1)%4, (id+1)%4]
			for neighbor in neighbors:
				if self.active[neighbor]['tx'] != None:
					return True
			return False

