import random
import time
import station
import time


class NullMac(station.Station):
	'''
	`NullMac` is essentially having no MAC protocol. The node sends
	whenever it has a packet ready to send, and tries up to two retries
	if it doesn't receive an ACK.

	The node makes no attempt to avoid collisions.
	'''
	def __init__(self, id, q_to_ap, q_to_station, interval, header):
		super().__init__(id, q_to_ap, q_to_station, interval)

	def run(self):
		# Continuously send packets
		while True:
			# Block until there is a packet ready to send
			self.wait_for_next_transmission()
			n = 0

			# Try up to three times to send the packet successfully
			while True:

				self.send('DATA', header)

				# Wait for a possible ACK. If we get one, we are done with this
				# packet. If all of our retries fail then we just consider this
				# packet lost and wait for the next one.
				recv = self.receive()

				if recv == 'ACK':
					break

				if n >= 3:
					break

				n += 1


class NullMacExponentialBackoff(station.Station):
	'''
	`NullMacExponentialBackoff` extends the basic NullMac to add exponential
	backoff if a packet is sent and an ACK isn't received.

	The sender should use up to two retransmissions if an ACK is not received.
	'''
	def __init__(self, id, q_to_ap, q_to_station, interval, header):
		super().__init__(id, q_to_ap, q_to_station, interval)

	def run(self):
		# Continuously send packets
		while True:
			# Block until there is a packet ready to send
			self.wait_for_next_transmission()
			n = 0

			while True:

				time.sleep(0.01 * random.randint(0, (2 ** n) - 1))
				self.send('DATA', header)
				recv = self.receive()

				if recv == 'ACK':
					break

				if n >= 3:
					break

				n += 1


class CSMA_CA(station.Station):
	'''
	`CSMA_CA` should implement Carrier Sense Multiple Access with Collision
	Avoidance. The node should only transmit data after sensing the channel is
	clear.
	'''
	def __init__(self, id, q_to_ap, q_to_station, interval, header):
		# print("interval is: ", interval)
		super().__init__(id, q_to_ap, q_to_station, interval)

	def run(self):
		# Continuously send packets
		while True:
			# Block until there is a packet ready to send
			self.wait_for_next_transmission()
			k = 0

			while True:

				if self.sense() is False:
					time.sleep(0.00005)

					if self.sense() is False:
						randomNum = random.randint(0, (2 ** k) - 1)

						while randomNum > 0:
							time.sleep(0.01)

							if self.sense() is False:
								randomNum -= 1
							else:
								while True:
									if self.sense() is False:
										randomNum -= 1
										break


						self.send('DATA', header)
						recv = self.receive()

						if recv == 'ACK':
							break

						if k >= 3:
							break

						k += 1


class RTS_CTS(station.Station):
	'''
	`RTS_CTS` is an extended CSMA/CA scheme where the transmitting station also
	reserves the channel using a Request to Send packet before transmitting. In
	this network, receiving a CTS message reserves the channel for a single DATA
	packet.
	'''
	def __init__(self, id, q_to_ap, q_to_station, interval, packet_size, packet_header):
		super().__init__(id, q_to_ap, q_to_station, interval, packet_size, packet_header)
		self.packet_size = packet_size
		self.header = packet_header


	def run(self):
		# Continuously send packets
		alpha = 0.01
		header = self.header

		while True:
			# Block until there is a packet ready to send
			self.wait_for_next_transmission()
			k = 0

			while True:

				if self.sense() is False:
					time.sleep(0.000001*alpha*self.packet_size)					 # DIFS from online wiki (50 us for IEEE 802.11b)
					# time.sleep(0.00005)

					if self.sense() is False:
						randomNum = random.randint(0, (2 ** k) - 1)

						while randomNum > 0:

							# time.sleep(0.01*alpha*self.packet_size)
							time.sleep(0.01)

							if self.sense() is False:
								randomNum -= 1
							else:
								while True:
									if self.sense() is False:
										randomNum -= 1
										break

						self.send('RTS', header)
						recv = self.receive()

						if recv == 'CTS':

							# while loop because if no ACK is received by the AP then it deadlocks.
							# If the ACK is sent and then immediately breaks, the reservation is never freed

							while recv is not 'ACK':
								self.send('DATA', header)
								recv = self.receive()

							break
							
						if k >= 3:
							break

						k += 1
						
