import socket, struct, sys
import numpy as np

class sr800:

    def __init__(self, addr='172.18.0.140'):
        self.header = [0xAA,0x01]
        self.code_sp = [0x06]  # Service code send parameter
        self.size = [0x00,0x0A]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10.0)
        self.sock.connect((addr,5200))
        self.sock.settimeout(None)

    def __del__(self):
        self.sock.close()
        
    def float_2_hex(self,Tset):
        return(hex(struct.unpack('<I', struct.pack('<f', Tset))[0]))
    
    def calc_checksum(self,hex_array):
        # Checksum per trial and error
        return([256 - np.mod(sum(hex_array[0:-1]),256)])


    def set_temperature(self,T):
        print(T)
        thex = bytes.fromhex(self.float_2_hex(T)[2:]) # ???
        tdec = list(map(lambda x: x, thex))

        self.code_st = [0x07,0xf1]  # Parameter 1: Blackbody set absolute
        self.param_size = [0x00,0x04] # Parameter size
        self.size = [0x00,0x0A]
        
        st11 = self.header.copy()
        st11.extend(self.size)
        st11.extend(self.code_sp)
        st11.extend(self.code_st)
        st11.extend(self.param_size)
        st11.extend(tdec)
        cs = self.calc_checksum(st11)
        st11.extend(cs)
        st1 = bytes(st11)
        print(T, st11)
        #st1 = b'\xAA\x01\x00\x0A\x06\x07\xF1\x00\x04\x42\xC8\x00\x00\x3F'
        self.sock.send(st1)

    def get_temperature(self):
#        st = [0xAA,0x01,0x00,0x0A,0x08,0x07,0xF0,0x00,0x00,0x07,0xD7,0x00,0x00,0x6E]
        st = [0xaa,0x01,0x00,0x16,0x88,0x07,0xd5,0x00,0x00,0x07,0xf0,0x00,0x00,0x07,0xd7,0x00,0x00,0x07,0xd9,0x00,0x00,0x07,0xf3,0x00,0x00,0x2c]
        self.sock.send(bytes(st));
#        import ipdb
#        ipdb.set_trace()
        ans = self.sock.recv(1024);
#        T = struct.unpack('>f', b''.join((ans[14:16],ans[12:14])))
        T = struct.unpack('>f', ans[22:26])
#        T = struct.unpack('>f', b''.join((ans[24:26],ans[22:24])))
#        thex = b''.join((ans[14:16],ans[13:11:-1]))
#        tbin = bin(struct.unpack('>I', b''.join((ans[14:16],ans[12:14])))[0])
#        tbin2 = bin(struct.unpack('>I', ans[12:16])[0])
#        return(T,thex,tbin, tbin2)
        return(T[0])

    def get_stability(self):
        st = [0xAA, 0x01, 0x00, 0x06, 0x08, 0x07, 0xd5, 0x00, 0x00, 0x6b]

        self.sock.send(bytes(st));
        ans = self.sock.recv(1024);
        if struct.unpack('>I', ans[-5:-1])[0] == 1:
            return(True)
        else:
            return(False)
        
## Antwort holen mit self.sock.recv(124) (SR800 Laenge max 1024 Bytes).
# Beispiel im Manual 

if __name__ == '__main__':
    s8 = sr800()
    if len(sys.argv) == 2:
        s8.set_temperature(float(sys.argv[1]))
    print(s8.get_temperature())
    print(s8.get_stability())


        
