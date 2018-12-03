import sys
import socket
import random
import getopt

import Checksum
import BasicSender


class InteractiveSender(BasicSender.BasicSender):
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))

    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    def start(self):
        seqno = 0
        msg_type = None
        while not msg_type == 'end':
            msg = raw_input("Message:")

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif msg == "done":
                msg_type = 'end'

            packet = self.make_packet(msg_type, seqno, msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive()
            self.handle_response(response)

            seqno += 1


if __name__ == "__main__":
    def usage():
        print "ADHS Interactive Sender"
        print "Type 'done' to end the session."
        print "-p PORT | --port=PORT The destination port, defaults to 30001"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "p:a:", ["port=", "address="])
    except:
        usage()
        exit()

    port = 30001
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a

    s = InteractiveSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
