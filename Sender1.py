import sys
import getopt

import Checksum
import BasicSender

class Sender(BasicSender.BasicSender):
    
    
    packets = [None] * 5                    
    packetsfilled = 0                      
    seqno =0                               
    msg_type =""                         
    
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)
            

    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet


    def start(self):
        global packets
        global packetsfilled 
        global msg_type
        global seqno
        
        packets = [None] * 5               
        packetsfilled = 0                  
        seqno =0                           
        msg_type =""                      
        
        while not msg_type == 'end':       
            self.fill_array()
            
            
                                                     
            self.send_packets_from_to(frm=0, to=packetsfilled)  
            
            
            completedWindow = False                                             
            while not completedWindow == True:                                 
            
                received_acks = [None] * 5                                      
                for x in range (0, packetsfilled):                              
                    received_acks[x]= self.receive(timeout=0.5)                
                    # self.handle_response(received_acks[x])
                if msg_type == 'end':                                           
                    print "Transfer Complete!"
                    break
                   
                
                self.parse_acks(acks=received_acks)                             
                # print received_acks
              
                error = self.check_for_error(acks = received_acks)  
                            
                if not error == -1:                                            
                    print "ERROR!"
                    if error < 10:  
                        
                     
                        print "Resolved into timeout"
                        self.send_packets_from_to(frm = error, to = packetsfilled)
                    else:
                        
                        
                        index = error - 10                                                      
                        print "Resolved into duplicate is at index %d" % index
                        if not int(received_acks[index])==seqno:                                
                            self.send_packets_from_to(frm = error-10, to = packetsfilled)
                        else:
                            
                           
                            completedWindow = True
                elif self.completed_window(acks = received_acks) == True:
                    completedWindow = True
            
        self.infile.close()
        
        
   
    def check_for_error(self, acks=[]):
        for i in range(4):
            if acks[i] is None:
                return i
            elif acks[i+1] is None:
                return i+1
            else:
                first = int(acks[i])
                second = int(acks[i+1])
                if(first == second):
                    return 10+i
        return -1
    
    
   
    def completed_window(self, acks = []):
        for i in range(5):
            if acks[i] == None:
                return False
        return True


    def parse_acks(self, acks=[]):
        for i in range(5):
            if(acks[i] is not None):
                msg_type, acknb, data, checksum  = self.split_packet(message = acks[i])
                acks[i] = acknb 
            
   
    def fill_array(self):
        global packets
        global msg_type
        global seqno
        global packetsfilled
        
        
        packetsfilled = 0       
        packets = [None] * 5    
        for x in range (0, 5):
            if msg_type == 'end':                                  
                break
            msg = self.infile.read(1450)                            
            msg_type = 'data'
            if seqno == 0:                                         
                msg_type = 'start'
            elif msg == "":
                msg_type = 'end'
            packet = self.make_packet(msg_type,seqno,msg)           
            packets[x] = packet                                     
            seqno += 1                                             
            packetsfilled += 1                                      

    def send_packets_from_to(self, frm, to):
        global packets
        for i in range (frm, to):
            msg_type, s, data, checksum  = self.split_packet(message = packets[i])
            self.send(packets[i])
   
    def log(self, msg):
        if self.debug:
            print msg

if __name__ == "__main__":
    def usage():
        print "ADHS Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 30001
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
