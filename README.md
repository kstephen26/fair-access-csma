# fair-access-csma

System Architecture and Running Our Code

In order to create a modified file sharing network, we peer under the hood of an existing Collision Avoidance simulation that we gleaned from the following code library: LINK. The simulation is organized using the following files to initialize users, use MAC protocols, and follow packets from their source to destination among multiple users. To run our modified code, execute $ python3 project.py, which in turn calls the other three files in this library. User parameters can be adjusted in project.py, whereas controller parameters can be modified (i.e. to call different modifications of the network) in access_point.py.

Mac.py: Provides the specifications for each MAC address sending information over the network, as well as the protocols that each MAC address uses to send packets. Each MAC protocol class in MAC, for example the RTS_CTS class, is an instance of a station class that specifies how a station using this MAC protocol sends packets.

Station.py: Specifies general requirements for a user to send information over a network. We use this file by calling instances of station through mac.py.

Access_point.py: The controller of the network that sends packets from sender to receiver and, for the RTS_CTS protocol, determines which users gain access to the network by distributing CTS messages to users randomly.

Project.py: The file we use to execute the program. This file specifies the number of users on the network, the MAC protocol(s) being used by each user, and the packets being sent by each user and calls the other three files in order to construct a network.
