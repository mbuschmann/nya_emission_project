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
a = requests.get('http://192.168.178.34/cgi/relaySt?Rel=0')
print(a.content)
