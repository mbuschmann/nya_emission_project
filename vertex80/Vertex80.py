import requests,os,time,sys
from time import sleep

class Vertex80():

    def __init__(self):
        self.default_meas()
        self.motor_com = "COM3"
        self.url_ftir = 'http://172.18.0.110'
        self.stat_htm = '/'.join((self.url_ftir,'stat.htm'))
        self.cmd_htm = '/'.join((self.url_ftir,'cmd.htm'))
        self.diag_htm = '/'.join((self.url_ftir, 'diag.htm'))
        self.data_htm = '/'.join((self.url_ftir, 'datafile.htm'))
        self.init_params = {'CNM':'AUTO Vertex',
                            'FLP': 0,
                            'SRC': 0}
        html_line = '&'.join(['='.join((x[0].strip(), str(x[1]).strip())) for x in self.init_params.items()])
        meas_command = '/'.join((self.url_ftir,self.cmd_htm))
        print('?'.join((self.cmd_htm,html_line)))
        requests.get('?'.join((self.cmd_htm,html_line)))
        
    def default_meas(self): 
        self.meas_params =  {'FLP': 0,
                            'SNM': 'test',
                            'CNM': 'AUTO Vertex',
                            'REP': 1,
                            'APT': 4000,
                            'NSS': 20,
                            'RES': 0.08,
                            'BMS': 1,
                            'VEL': 20000,
                            'SRC': 201,
                            'AQM': 'SD',
                            'CHN': 1,
                            'DTC': 16416,
                            'HPF': 0,
                            'LPF': 20000,
                            'OPF': 1,
                            'PGN': 2,
                            'DEL': 0,
                            'WRK': 1,
                            'PHR': 2.0,
                            'COR': 0,
                            'GNS': 1}

    def set_samplename(self, name):
        self.meas_params['SNM'] = name

    def set_sampleform(self,name):
        self.meas_params['SFM'] = name

    def get_status(self):
        status={}
        stat = requests.get(self.stat_htm)
        # the statues variable
        i1 = stat.text.rfind('ID=MSTCO')
        i2 = stat.text.find('<', i1)
        status['status'] = stat.text[i1 + 9:i2]
        i1 = stat.text.rfind('ID=SCAN')
        if i1 > 0:
            i2 = stat.text.find('<', i1)
            status['scans'] = int(stat.text[i1 + 8:i2])
        else:
            status['scans'] = 0
        i1 = stat.text.rfind('ID=SRSC')
        i2 = stat.text.find('<', i1)
        status['restscans'] = int(stat.text[i1 + 8:i2])
        #
        diag = requests.get(self.diag_htm)
        i1 = diag.text.rfind('ID=DIAG_DTC_STAT')
        i2 = diag.text.find('>', i1)
        i3 = diag.text.find('<', i1)
        status['detector'] = diag.text[i2+1:i3]

        data = requests.get(self.data_htm)
        i1 = data.text.find('Datafile status')
        i2 = data.text.find('<TD>', i1)
        i3 = data.text.find('</TD>', i2)
        status['datafile'] = data.text[i2+4:i3]
        return (status)

    def measure(self):
        html_line = '&'.join(['='.join((x[0].strip(), str(x[1]).strip())) for x in self.meas_params.items()])
        meas_command = '/'.join((self.url_ftir,self.cmd_htm))
        print('?'.join((self.cmd_htm,html_line)))
        requests.get('?'.join((self.cmd_htm,html_line)))

    def get_data(self, filename):
        status = self.get_status()
        if status['datafile']=='Ready for download':
            data = requests.get(self.data_htm)
            i1 = data.text.find('A HREF=')
            i2 = data.text.find('">', i1)
            print('/'.join((self.url_ftir,data.text[i1+9:i2])))
            data = requests.get('/'.join((self.url_ftir,data.text[i1+9:i2])))

            with open(filename, 'wb') as fid:
                print (fid)
                fid.write(data.content)
            
if __name__=='__main__':
    
    
    v80 = Vertex80()
#    status = v80.get_status()
    v80.measure()
    while v80.get_status()['status'] != 'IDL':
        sleep(1)
        print(v80.get_status()['status'])
        print(v80.get_status()['datafile'])
        pass
    v80.get_data('C:\\Users\\ftir\\Desktop\\nya_emission_project\\vertex80\\test.0')
