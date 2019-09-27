from __future__ import print_function, division
import os, sys, time
import datetime as dt
from PyQt5.QtGui import QIcon
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import requests
scriptpath = os.path.dirname(os.path.abspath(__file__))
#print(scriptpath)
#scriptpath = 'C:/Users/ftir/Desktop/nya_emission_project'
sys.path.append(os.path.join(scriptpath, '..', 'ftsreader'))
sys.path.append(os.path.join(scriptpath, 'motorcontrol'))
sys.path.append(os.path.join(scriptpath, 'blackbody'))
sys.path.append(os.path.join(scriptpath, 'vertex80'))
sys.path.append(os.path.join(scriptpath, 'gui'))
from blackbodymotor_pytmcl import motorctrl
from sr80 import sr80
from Vertex80 import Vertex80
from ftsreader import ftsreader
from multiprocessing import Process, Manager

class NyaEM():
    def __init__(self, folder='Z:/out/'):
        super().__init__()
        self.folder = os.path.abspath(folder)
        self.filename = 'testfilename'

        #
        if sys.platform.startswith('win'):
            self.motor_com = "COM3"
        elif sys.platform.startswith('linux'):
            self.motor_com = "/dev/ttyACM1"
        self.stat_htm = 'http://172.18.0.110/stat.htm'

        #
        self.initinstruments()
        #
        self.act_filename = ''
        # Variable used by run_sequence()
        self.entry = 1  # start always at the beginning of the sequence
        self.run_seq = False # True if a sequence is running
        self.act_entry = 1 # contains the number of the entry worked on
        self.measurement = False # True if a measurement is under way
        self.measurement_repeat = False
        self.wait = False # True if a wait statement is active
        self.time_continue = dt.datetime.now() # initialize timer variable, this is used in the wait time

        self.sequence = {1: 'reinit_motor',
                    2: 'folder Z:\\out\\',
                    3: 'set sr80 temperature 100.0',
                    4: 'bb point sr80',
                    5: 'wait T stable',
                    6: 'measure 10',
                    7: 'set sr80 temperature 20.0',
                    8: 'wait T stable',
                    9: 'measure 10',
                    10: 'bb point park',
                    11: 'repeat 3'}

        self.sequence = {1: 'set folder Z:\\out\\',
                        2: 'reinit motor',
                        3: 'set motor roof',
                        4: 'measure start',
                        5: 'set sr80 25.0',
                        6: 'wait SR80 stable',
                        7: 'measure stop',
                        8: 'set motor sr80',
                        9: 'measure start',
                        10: 'wait time 5 min',
                        11: 'measure stop',
                        12: 'set sr80 20.0',
                        13: 'loop 3'}

        self.sequence = {1: 'reinit motor',
                         2: 'set motor park',
                         3: 'set sr80 20.0',
                         4: 'wait sr80 stable',
                         5: 'set motor sr80',
                         6: 'measure start',
                         7: 'measure repeat',
                         8: 'wait time 10',
                         9: 'measure stop',
                         10: 'set sr80 100.0',
                         11: 'set motor roof',
                         12: 'measure start',
                         13: 'measure repeat',
                         14: 'wait sr80 stable',
                         15: 'measure stop',
                         16: 'set motor sr80',
                         17: 'measure start',
                         18: 'measure repeat',
                         19: 'wait time 10',
                         20: 'measure stop',
                         21: 'set sr80 20.0',
                         22: 'set motor roof',
                         23: 'measure start',
                         24: 'measure repeat',
                         25: 'wait sr80 stable',
                         26: 'measure stop',
                         27: 'loop 5'}

    def start_sequence(self):
        self.run_seq = True
        self.entry = 1 # start sequence at position 1

    def stop_sequence(self):
        self.run_seq = False
        self.motor.park()
        self.setsr80temp(20.0)

    def run_sequence(self):
        if not self.run_seq:
            return()
        nr_entry = len(self.sequence)
        unknown = False # unknown should never become true
        if self.measurement_repeat:
            self.repeat_measure()
        while True:
            # read entry
            command = self.sequence[self.entry].split()
            print(self.entry, self.sequence[self.entry])
            self.entry += 1
            if self.measurement_repeat:
                self.repeat_measure()
            if command[0] == 'reinit':
                if command[1] == 'motor':
                    self.reinitmotor(1)
                else:
                    unknown = True
            elif command[0] == 'set':
                if command[1] == 'sr80':
                    self.setsr80temp(float(command[2]))
                if command[1] == 'motor':
                    if command[2] == 'sr80':
                        self.motor.blackbody()
                    elif command[2] == 'roof':
                        self.motor.roof()
                    elif command[2] == 'park':
                        self.motor.park()
                    else:
                        unknown = True
            elif command[0] == 'measure':
                if command[1] == 'start':
                    self.start_measure()
                elif command[1] == 'stop':
                    self.measurement_repeat = False
                    stat = self.v80.get_status()
                    if stat['status'] == 'IDL':
                        self.stop_measure()
                    else:
                        self.entry -= 1
                        break
                elif command[1] == 'repeat':
                    self.measurement_repeat = True
            elif command[0] == 'wait':
                if command[1] == 'sr80':
                    # wait for sr80 to stabilize
                    # self.SR80_stable is set by
                    self.Temperature_reached()
                    if not self.SR80_stable:
                        self.entry -= 1
                        break
                    else:
                        pass
                elif command[1] == 'time':
                    # Set a timer, goes on only after the time is more than self.time_continue
                    print(self.time_continue)
                    print(dt.datetime.now())
                    if dt.datetime.now() < self.time_continue:
                        self.entry -= 1
                        break
                    else:
                        # if a timer has been active, go to next line.
                        # if timer has been set now, go back to this line
                        if self.wait:
                            self.wait = False
                        else:
                            tt = float(command[2])
                            self.time_continue = dt.datetime.now() + dt.timedelta(seconds=tt)
                            self.wait = True
                            self.entry -= 1
            elif command[0] == 'loop':
                self.entry = int(command[1])
            else:
                unknown = True

    def start_measure(self):
        self.measurement = True
        if self.motor.position == 'roof':
            fname = 'nyem'+dt.datetime.now().strftime('%Y%m%d%H%M%S')+'_up.000'
            self.v80.set_sampleform('UP')
            self.v80.set_samplename('HUTCH UNKNOWN')
        elif self.motor.position == 'bb':
            fname = 'nyem'+dt.datetime.now().strftime('%Y%m%d%H%M%S')+'_bb_%3.2f.000'%(self.bbtemp)
            self.v80.set_sampleform('SR80')
            self.v80.set_samplename('%.5f +/- %.5f'%(self.bbtemp,selfbbstdv))
        else:
            fname = 'nyem' + dt.datetime.now().strftime('%Y%m%d%H%M%S') + '_xx.000'

        path = os.path.join(self.folder, dt.datetime.now().strftime('%Y%m%d'))
        if not os.path.exists(path):
            os.mkdir(path)
        self.act_filename = os.path.join(path,fname)
        self.v80.measure()

    def repeat_measure(self):
        stat = self.v80.get_status()
        if stat['status'] == 'IDL':
            self.save_measurement()
            self.start_measure()

    def stop_measure(self):
        self.measurement = False
        self.save_measurement()
        pass

    def save_measurement(self):
        print(self.act_filename)
        self.v80.get_data(self.act_filename)

    def initinstruments(self):
        self.sr80 = sr80()
        self.motor = motorctrl(self.motor_com)
        self.v80 = Vertex80()
        self.maxnumber = 1
        t = -999
        while  t == -999:
            t = self.sr80.get_temperature()
            time.sleep(1)
        self.bbtemp = t

    def setv80param(self):
        l = self.paramtextbox.text().split('|')
        li = [i.split(':')[0].strip() for i in l]
        lj = [i.split(':')[1].strip() for i in l]
        for i,j in zip(li, lj):
            if i in ['AQM']:
                self.v80.meas_params[i] = j.strip()
            elif i in ['RES', 'PHR']:
                self.v80.meas_params[i] = float(j.strip())
            else:
                self.v80.meas_params[i] = int(j.strip())
        for i, j in self.v80.meas_params.items():
            print(i,':',j)

    def setsr80temp(self,new_T):
        self.bbtemp = new_T
        print ('setsr80temp',self.bbtemp)
        self.sr80.set_temperature(self.bbtemp)


    def reinitmotor(self, item):
        self.motor.init_motor()

    def getfolder(self):
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        print('Opening ', self.folder)

    def setcheckbox(self, state):
        if state == QtCore.Qt.Checked:
            self.checkbox = True
        else:
            self.checkbox = False

    def get_ifg(self):

        self.last_ifg_fname = self.act_filename
        try:
            self.lastifg = ftsreader(self.last_ifg_fname, getspc=True, getifg=True)
        except Exception as e:
            print(e)
            self.lastifg = 0

#    def _update_canvas(self):
#        #print('Plotting ', self.filename)
#        self._dynamic_ax1.clear()
#        self._dynamic_ax2.clear()
#        self.get_ifg()
#        self._dynamic_ax1.set_title('Latest measurement ' + self.act_filename)
#        try:
#            sx = self.lastifg.spcwvn
#            sy = self.lastifg.spc
#            spc = True
#        except:
#            spc = False
#        try:
#            iy = self.lastifg.ifg
#            ifg = True
#        except:
#            ifg = False
#        if ifg:
#            self._dynamic_ax1.plot(iy, 'k-')
#            self._dynamic_ax1.figure.canvas.draw()
#        else:
#            print(self.last_ifg_fname, ' --> no Interferogram found')
#        if spc:
#            self._dynamic_ax2.plot(sx, sy, 'k-')
#            self._dynamic_ax2.figure.canvas.draw()
#        else:
#            print(self.last_ifg_fname, ' --> no Spectrum found')

#    def updateprogressbar(self, s):
#        self.statusBar().showMessage(s)



    def Temperature_reached(self):
        t = self.sr80.get_stability()
        if np.abs(t[0] - self.bbtemp) < 0.1 and np.abs(t[1] < 0.1) :
            self.SR80_stable = True
        else:
            self.SR80_stable = False
        return(t[0], t[1], self.SR80_stable)
