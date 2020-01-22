#! /usr/bin/python3


import threading,socket,re,mimetypes,os
import sqlite3


ListFiles = ['/','/css/style.css','/js/main.js','/main.html'] # les fichiers autorisés à être lu
BddFile = 'data.bdd.sqlite'

class HttpServer(threading.Thread):
	def __init__(self,host='127.0.0.1',port=8081):
		threading.Thread.__init__(self)
		self.method = None
		self.status = None
		self.url = None
		self.body = ''
		self.version = 'HTTP/1.1'
		self.headers = {}
		self.server = None
		self.state = True
		self.bdd = BddFile

		try:
			self.conn = sqlite3.connect(self.bdd)
			self.conn.execute('''CREATE TABLE IF NOT EXISTS
      packets (ID INTEGER PRIMARY KEY AUTOINCREMENT,
      MACSOURCE CHAR(20),
      MACDESTINATION CHAR(20),
      IPSOURCE CHAR(20),
      IPDESTINATION CHAR(20),
      PORTSOURCE INT,
      PORTDESTINATION INT,
      TTL INT,
      LENG INT);''')
			self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
			self.socket.bind((host,port))
			self.socket.listen(10)
		except socket.error:
			print('[ERROR] Impossible de créer le server HTTP')
			self.socket.close()
			exit(-1)

	def run(self):
		while self.state:
			client, addr = self.socket.accept()
			print('[INFO] Nouveau client : ',addr)
			data = client.recv(1024).decode('utf-8')
			if(self.GetDataRequest(data)): self.SendResponse(client)
			client.close()
			print('[INFO] Client Quit : ',addr)

# Envoi des informations au client
	def SendResponse(self,client):
		client.send(b'%s %s\r\n'%(self.version.encode('utf-8'),self.status.encode('utf-8')))
		for i in self.headers.keys():
			client.send('{}: {} \r\n'.format(i,self.headers[i]).encode('utf-8'))
		client.send(b'\r\n')
		client.send(self.body.encode('utf-8'))


	def MakeClientResponse(self,data):
		self.body = data
		self.headers = {
			'Server:':'Soli-Server',
			'Host:' : socket.gethostbyname(socket.gethostname()),
			'Content-type:': 'text/txt; charset=UTF-8',
			'Content-Length:': len(self.body)
		}
		self.status = self.status = '200 OK'
		self.version = 'HTTP/1.1'


	def ExecCommand(self,cmd):
		if(cmd == '/size'):
			cmd = "SELECT COUNT(*) FROM packets"
			self.conn.execute(cmd)
			row = self.conn.commit()
			print(row)
			self.MakeClientResponse('200')
			return True
		return False


# Prepare la requette reçu pour envoi
	def ExecRequest(self):
		self.body = ''
		if(self.method == None or self.url == None): return False
		if( self.ExecCommand(self.url)==True): return

		if(self.url == '/' or self.url == ''): self.url = '/main.html'
		if(os.path.isdir(self.url) == False and os.path.exists('./html'+self.url) == True and (self.url in ListFiles)==True):
			f = open('./html'+self.url,'r')
			self.body = f.read()
			f.close()
			self.headers = {
				'Server:':'Soli-Server',
				'Host:' : socket.gethostbyname(socket.gethostname()),
				'Content-type:': mimetypes.guess_type(self.url)[0]+'; charset=UTF-8',
				'Content-Length:': len(self.body)
			}
			self.status = '200 OK'
		else:
			self.body = '<b>404 NOT FOUND</b>'
			self.headers = {
				'Server:':'Soli-Server',
				'Host:' : socket.gethostbyname(socket.gethostname()),
				'Content-type:': 'text/html; charset=UTF-8',
				'Content-Length:': len(self.body)
			}
			self.status = '404 Not Found'
			self.version = 'HTTP/1.1'
			if self.url == '/stop': 
				self.state=False
				self.body = '<b>Serveur Stop command</b>'

	

# Recupere les informations de la requette reçu par le server
	def GetDataRequest(self,data):
		if (data == '' or data == None or type(data) != str ): return None
		data = data.split('\r\n')
		req = data[0].split(' ')
		self.headers.clear()
		self.method = self.status = self.url = None
		if(len(req)>2):
			self.method = req[0]
			self.url = req[1]
			self.version = req[2] or 'HTTP/1.1'
			for i in range(1,len(data)):
				el = re.match(r'^[a-zA-Z.-]+: ',data[i])
				if el != None:
					self.headers[el[0].strip()] = data[i].replace(el[0],'').strip()
			self.ExecRequest()
			return True
		return False