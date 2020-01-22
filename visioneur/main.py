#! /usr/bin/python3

import HttpServer
import SnifferIP


if __name__ == '__main__':
  http = HttpServer.HttpServer()
  #snif = SnifferIP.IPSniffing()
  http.start()
  #snif.start()
  print('[INFO] is running ...')




