#! /usr/bin/python3

import re,struct,socket,threading,sqlite3

class IPSniffing(threading.Thread):
  def __init__(self,interf='lo',protocol=0x3,bdd='./data.bdd.sqlite'):
    try:
      # Création de la socket pour sniffer
      threading.Thread.__init__(self)
      self.sniff = socket.socket(socket.PF_PACKET,socket.SOCK_RAW,socket.htons(protocol))
      self.sniff.bind((interf,0))
      #self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
      #self.server.bind(('',8082))
      print('[INFO] Initialisation du sniffer OK !')
      # Initialisation de la base de données
      self.bdd = bdd
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
      print('[INFO] Initilialisation de la base de donnée OK !')
    except socket.error:
      print('[ERROR] Impossible de continuer NOK !')
      exit(-1)

  def run(self):
    while True:
      data = self.sniff.recv(1024)
      packet = struct.unpack('!6s6sH',data[0:14])
      if(packet[2]==0x800): # package IP
        mac_destination = ':'.join(["%.2X"%(e) for e in packet[0]])
        mac_source = ':'.join(["%.2X"%(e) for e in packet[1]])
        packet = struct.unpack('!BBHHHBBH4s4s',data[14:34])
        tabproto= {
          1:'ICMP',2:'IGMP',6:'TCP',17:'UDP'
        }
        length = packet[2]
        proto = packet[6]
        if proto in tabproto.keys(): proto = tabproto[packet[6]]
        ip_source = '.'.join([str(int(e)) for e in packet[8]])
        ip_destination = '.'.join([str(int(e)) for e in packet[9]])
        port_source = (struct.unpack('!H',data[34:36])[0])
        port_destination = struct.unpack('!H',data[36:38])[0]
        cmd = "INSERT INTO packets (MACSOURCE,MACDESTINATION,IPSOURCE,IPDESTINATION,PORTSOURCE,PORTDESTINATION,TTL,LENG) VALUES ('%s','%s','%s','%s',%d,%d,%d,%d)"%(mac_source,mac_destination,ip_source,ip_destination,int(port_source),int(port_destination),64,length)
        self.conn.execute(cmd)
        self.conn.commit()
        #print('%s %s %s %s %s %s %s %s #\n'%(mac_source,mac_destination,ip_source,port_source,ip_destination,port_destination,proto,length))


if __name__ == '__main__':
  sn = IPSniffing()
  sn.run()
