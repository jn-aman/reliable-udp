import sys
import socket
import random

import Checksum


class BasicSender(object):
    def __init__(self,dest,port,filename,debug=False):
        self.debug = debug
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None) # blocking
        self.sock.bind(('',random.randint(10000,40000)))
        if filename == None:
            self.infile = sys.stdin
        else:
            self.infile = open(filename,"r")

    def receive(self, timeout=None):
        self.sock.settimeout(timeout)
        try:
            return self.sock.recv(4096)
        except (socket.timeout, socket.error):
            return None

    def send(self, message, address=None):
        if address is None:
            address = (self.dest,self.dport)
        self.sock.sendto(message, address)

    def make_packet(self,msg_type,seqno,msg):
        body = "%s|%d|%s|" % (msg_type,seqno,msg)
        checksum = Checksum.generate_checksum(body)
        packet = "%s%s" % (body,checksum)
        return packet

    def split_packet(self, message):
        pieces = message.split('|')
        msg_type, seqno = pieces[0:2] 
        checksum = pieces[-1] 
        data = '|'.join(pieces[2:-1])
        return msg_type, seqno, data, checksum

    def start(self):
        raise NotImplementedError
