import sys
import requests

#requests.get('http://192.168.178.34/cgi/toggleRelay?Rel=0')
#requests.get('http://192.168.178.34/cgi/getPower?Pow=0')
#a = requests.get('http://192.168.178.34/cgi/getPower?Pow=0')
#print(a.content)
#http://192.168.178.34/cgi/relaySt?Rel=0
#http://192.168.178.34/cgi/relaySt?Rel=1
#http://192.168.178.34/cgi/toggleRelay?Rel=0
#http://192.168.178.34/cgi/toggleRelay?Rel=1
#http://192.168.178.34/cgi/getPower?Pow=0
#http://192.168.178.34/cgi/isTempHw
#http://192.168.178.34/cgi/logoff
#http://192.168.178.34/cgi/isFlashFs
#http://192.168.178.34/cgi/getTemp
#http://192.168.178.34/cgi/getPower?Pow=1
#a = requests.get('http://172.18.0.150/cgi/relaySt?Rel=0')
#print(a.content)

class brennenstuhl():
    def __init__(self, addr):
        self.addr = addr
        self.url = 'http://'+self.addr+'/cgi/'

    def send_cmd(self, cmd, switch):
        r = requests.get(self.url+cmd+'?Rel='+switch)
        return r.content.decode('utf8')

    def testswitch(self, switch):
        if switch in ['0', '1']:
            return True
        else:
            raise ValueError('Not a valid value for relay selection:', switch)
            return False

    def switch_off(self, switch):
        self.testswitch(switch)
        state = self.switch_state(switch)
        if state=='on':
            cmd = 'toggleRelay'
            r = self.send_cmd(cmd, switch)
        else:
            pass

    def switch_on(self, switch):
        self.testswitch(switch)
        state = self.switch_state(switch)
        if state=='off':
            cmd = 'toggleRelay'
            r = self.send_cmd(cmd, switch)
        else:
            pass

    def switch_state(self, switch):
        self.testswitch(switch)
        cmd = 'relaySt'
        r = self.send_cmd(cmd, switch)
        return r

if __name__=='__main__':
    usemsg = 'Usage:\n\t $ python brennenstuhl.py <switch> <arg>\n\n where <switch> is "0" or "1" and <arg> is "on" or "off" or "state"'
    # After power on, SR800 takes approx 20sec to boot up.
    if len(sys.argv)<3:
        print(usemsg)
    else:
        addr = '172.18.0.150'
        switch = sys.argv[1]
        arg = sys.argv[2]
        if switch in ['0', '1'] and arg in ['on', 'off', 'state']:
            pass
        else:
            exit(usemsg)
        BS = brennenstuhl(addr)
        if arg=='on':
            BS.switch_on(switch)
        elif arg =='off':
            BS.switch_off(switch)
        elif arg=='state':
            print(BS.switch_state(switch))
        else:
            exit()