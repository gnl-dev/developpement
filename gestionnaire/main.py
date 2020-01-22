#! /usr/bin/python3
# -*- coding:utf-8 -*-

import socket
import sys
import os
import re
import threading
import mimetypes
import sqlite3
import random
import sniffing


# Les fichiers autorisés à etre retourné par le service
AutorisedFiles = ['main.html','css/style.css','js/main.js']

#--------------------------------------------------------------------
# Format la requette reçu par le service, pour traitement
#--------------------------------------------------------------------
def FormatRequest(data,addr):
	try:
		data = data.split('\r\n')
		method = data[0].split(' ')
		url = method[1]
		version = method[2]
		method = method[0]
		headers = {}
		if(len(data)>1):
			for i in data[1:]:
				key = re.match(r'^[a-zA-Z-.]+:',i)
				if(key != None):
					key = key.group(0)
					headers[key.replace(':','')] = i.replace(key,'').strip()
		return method,url,version,headers
	except:
		print('[WARNING] Demande de requêtte rejetée pour : ',addr)
		return False
	return False
#--------------------------------------------------------------------
# Envoi des informations au client via HTML
#--------------------------------------------------------------------
def SendResponse(url,method,status,version,headers,body,client):
	client.send(b'%s %s\r\n'%(version.encode('utf-8'),status.encode('utf-8')))
	for i in headers.keys():
		client.send('{}: {} \r\n'.format(i,headers[i]).encode('utf-8'))
	client.send(b'\r\n')
	client.send(body.encode('utf-8'))

#--------------------------------------------------------------------
# Traite la requette et retoure la réponse
#-------------------------------------------------------------------
def ResponseMethod(req,client):
	# Gestion d'une methode GET
	method = req[0]
	url = req[1]
	version = version = 'HTTP/1.1'
	body = '501 NOT IMPLEMENTED'
	headers = {
		'Server:':'Soli-Server',
		'Host:' : socket.gethostbyname(socket.gethostname()),
		'Content-type:': 'text/plain; charset=UTF-8',
	}
	status = '501 Not Implemented'
	if(url == '/' or url == ''): url = 'main.html'
	url = re.sub(r'^\/','',url)
	print(url)
	try:
		if method == 'GET' and url.replace(r'^/','') in AutorisedFiles and os.path.isdir('./html/'+url) == False and os.path.exists('./html/'+url) == True:
			f = open('./html/'+url,'r')
			body = f.read()
			f.close()
			headers['Content-type:'] = mimetypes.guess_type(url)[0]+'; charset=UTF-8',
			status = '200 OK'


#--------------------------------------------------------------------
# Traite la gestion des Method CMD
#-------------------------------------------------------------------
		if method == 'CMD':
			# Demande le nombre de packets présent dans la table
			if url == 'nbpackets':
				status = '200 OK'
				req='SELECT COUNT(*) FROM packets'
				body = str(conn.execute(req).fetchone()[0])
				
			if url == 'lastpackets':
				status = '200 OK'
				req = 'SELECT * FROM packets ORDER BY id DESC LIMIT 10'
				a = conn.execute(req).fetchall()
				body = ''
				for e in a:
					body+='<div> {0} : [{1} > <b>{2}</b>] [<b>{3}</b>:{4}  >  {5}:{6}] [{7}] [<i>{8}</i>] </div>'.format(e[0],e[1],e[2],e[3],e[5],e[4],e[6],e[7],e[8])

#--------------------------------------------------------------------
# Erreur 404
#-------------------------------------------------------------------
	except:
		body = '<b>404 NOT FOUND</b>'
		headers['Content-type'] =  'text/plain; charset=UTF-8'
		status = '404 Not Found'

	headers['Content-Length:']= len(body)
	SendResponse(url,method,status,version,headers,body,client)


if __name__ == '__main__':
	print('[WARNING] Les droits admins sont requis pour le bon fonctionnement')
	print('[INFO] '+ re.search(r'/[a-zA-Z.]+$',sys.argv[0]).group(0),' <port> <bdd filename>')
	print('[INFO] Traitement en cours veuillez patienter ...')
	# Verification des arguments passés à la ligne de commande
	state = True
	try:
		port = int(sys.argv[1])
	except:
		port = 8081
	try:
		bddfile = sys.argv[2]
	except:
		bddfile = 'packets.bdd.sqlite'
	print('[INFO] Port en écoute : ',port)
	print('[INFO] Nom de la bdd ',bddfile)
	
	# Construction du socket principale
	try:
		mainsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # socket applicative IP
		mainsock.bind(('',port))
		mainsock.listen(30)
	# Initialisation de la bdd sqlite
		conn = sqlite3.connect(bddfile)
	except:
		print('[ERROR] Impossible de créer le serveur sur les éléments choisis')
		exit(-1)

	print('[INFO] Le service est disponible')
	while state:
		(client, addr) = mainsock.accept()
		data = client.recv(2048).decode('utf-8')
		req = FormatRequest(data,addr)
		if(req!=False):
			ResponseMethod(req,client)
		client.close()

