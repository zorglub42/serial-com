#!/usr/bin/python
# -*- coding: UTF-8 -*-

#--------------------------------------------------------
 # Module Name : socket server
 # Version : 1.0.0
 #
 # Software Name : SerialCom
 # Version : 1.0
 #
 # Copyright (c) 2015 Zorglub42
 # This software is distributed under the Apache 2 license
 # <http://www.apache.org/licenses/LICENSE-2.0.html>
 #
 #--------------------------------------------------------
 # File Name   : /usr/local/bin/arduino-controler.py
 #
 # Created     : 2015-12
 # Authors     : Zorglub42 <contact(at)zorglub42.fr>
 #
 # Description :
 #     Connect arduino through a serial port and allow communication
 #		to it from a TCP socket
 #--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
 
import sys
import select
import socket
import serial
import time
import threading	
 
class Server:
 
	# Contructeur de la class Server.
	#
	# @param port Port de connexion
	# @param listen Nombre de connexion en attente max
	# @param device Port serie pour communiquer avec l'arduino
	# @param baud Vitesse du port serie
	# @param verbose Mode bavard
	
	def __init__(self,address='',  port = 9999, listen = 5, device='/dev/ttyACM0', baud=9600, verbose=0):
		# Initialisation 
		self.nbClients = 0	# Nombre de client connecté
		self.sockets = []	# Liste des sockets client
 
		self.device=device
		self.baud=baud
		self.verbose=verbose
		
		
		
		# Création du socket serveur
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# On passe le socket serveur en non-bloquant
		self.socket.setblocking(0)
		# On attache le socket au port d'écoute. 
		self.socket.bind((address, port))
		# On lance l'écoute du serveur. "listen" est le nombre max de 
		# connexion quand la file d'attente
		self.socket.listen(listen)

		#On crée un sémaphone pour l'accès a l'arduino
		self.arduino=threading.BoundedSemaphore(1)
 
 
 
	# Surcouche de la fonction socket.recv
	# On utilise le système d'exeption de recv pour savoir si il reste
	# des donnees a lire
	#
	# @param socket Socket sur lequelle il faut recuperer les données
	# @return Données envoyées par le client
	def receive(self, socket):
		buf = "" # Variable dans laquelle on stocke les données
		_hasData = True # Nous permet de savoir si il y de données à lire
		while _hasData:
			# On passe le socket en non-bloquant
			socket.setblocking(0)
			try:
				_data = socket.recv(256)
				if(_data):
					buf += _data
				else:
					# Déconnexion du client
					_hasData = False
			except:
				_hasData = False
		return buf
 
 
 
	# Fonction qui lance les sockets et s'occupe des clients
	def run(self):
		# On ajoute le socket serveur à la liste des sockets
		ser = serial.Serial(self.device, self.baud, timeout=0.1)

		self.sockets.append(self.socket)
		# Go
		while True:
			try:
				# La fonction select prends trois paramètres qui sont la liste des sockets
				# Elle renvoie 3 valeurs
				# 	1- La liste des sockets qui ont reçus des données
				# 	2- La liste des sockets qui sont prêt à envoyer des données
				#	3- Ne nous interesse pas dans notre cas
				readReady ,writeReady, nothing = select.select(self.sockets, self.sockets, [])
			except select.error, e:
				break
			except socket.error, e:
				break
 
			# On parcours les sockets qui ont reçus des données
			for sock in readReady:
				if sock == self.socket:
					# C'est le socket serveur qui a reçus des données
					# Cela signifie qu'un client vient de se connecter
					# On accept donc ce client et on récupère qques infos
					client, address = self.socket.accept()
					if self.verbose:
						print("TCP-CLIENT.connect: " + client.getpeername()[0]);
						sys.stdout.flush()
					# On incrémente le nombre de connecté
					self.nbClients += 1
					# On ajoute le socket client dans la liste des sockets
					self.sockets.append(client)
				else:
					# Le client a envoyé des données, on essaye de les lire
					try:
						# On fait appelle à la surchage que l'on a écrite plus haut
						data = self.receive(sock).replace("\n","").replace("\r","")
						if data :
							#On verouille l'accès à l'arduino
							self.arduino.acquire();
							if self.verbose:
								print("TCP-CLIENT.send: " + data)
								sys.stdout.flush()

							ser.write(data + "\n");
							
							serial_line = ser.readline()
							clearLine=serial_line.replace("\n","").replace("\r","")
							while clearLine != "***START***":
								if self.verbose:
									print("ARDUINO.flushing: >" + clearLine + "<")
									sys.stdout.flush()
								serial_line = ser.readline()
								clearLine=serial_line.replace("\n","").replace("\r","")
							
							serial_line = ser.readline()
							clearLine=serial_line.replace("\n","").replace("\r","")
							while clearLine != "***DONE***":
								# l'arduino a envoyé qqch et que ce n'est pas la notif de fin On renvoi au client TCP ce que 
								if clearLine != '' and clearLine !="***DONE***":
									if self.verbose:
										print("ARDUINO.answer: >" + clearLine + "<")
										sys.stdout.flush()
									sock.send(serial_line)
								serial_line = ser.readline()
								clearLine=serial_line.replace("\n","").replace("\r","")
							#On libere l'accès à l'arduino
							
							print("End connection");
							self.arduino.release();

						# On diminu le nombre de client
						self.nbClients -= 1
						# On supprime le socket de la liste des sockets
						sock.close()
						self.sockets.remove(sock)
						if self.verbose:
							print("TCP-CLIENT.disconnect: ")
							sys.stdout.flush()
							
					except socket.error, e:
						self.sockets.remove(sock)
						self.arduino.release();
							

#Valeurs de parametrage par defaut
PORT=9999
QUEUE_SIZE=5
DEVICE='/dev/ttyACM0'
BAUD_RATE=9600
VERBOSE=False
ADDRESS=''


#Examen des parametres recu de la ligne de commande
for i, arg in enumerate(sys.argv):
		if arg == '-p':
			PORT=int(sys.argv[i+1])
		elif arg == '-q':
			QUEUE_SIZE=int(sys.argv[i+1])
		elif arg == '-d':
			DEVICE=sys.argv[i+1]
		elif arg == '-b':
			BAUD_RATE=int(sys.argv[i+1])
		elif arg == '-v':
			VERBOSE=True
		elif arg == '-a':
			ADDRESS=sys.argv[i+1]
			
print "Socks arduino server starting:"
print "	Device=" + DEVICE
print "	Baud=" + str(BAUD_RATE)
print "	TCP Port=" + str(PORT)
print "	Queue Size=" + str(QUEUE_SIZE)
sys.stdout.flush()

server = Server(ADDRESS, PORT, QUEUE_SIZE, DEVICE, BAUD_RATE, VERBOSE)
server.run()
