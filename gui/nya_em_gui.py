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
from nya_em import NyaEM


class nyaemgui(NyaEM, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #
        self.title = 'Ny-Ålesund Emission Measurements'
        self.setWindowTitle(self.title)
        #
        self.checkbox = False
        #
        self.initUI()
        #
        #        self._update_canvas()
        #
        self.bck = QtCore.QTimer()
        self.bck.setInterval(1000)
        self.bck.timeout.connect(self.Update_StatusBox)
        self.bck.start()

        self.rseq = QtCore.QTimer()
        self.rseq.setInterval(1000)
        self.rseq.timeout.connect(self.run_sequence)
        self.rseq.start()


    def write_sequence(self):

        for l in self.sequence:
            self.sequence_box.appendPlainText('%s %s'%(l,self.sequence[l]))

    def initMaintab(self):
        self._main.gridlayout = QtWidgets.QGridLayout()

        self.sequence_box = QtWidgets.QPlainTextEdit(self._main)
        #self.sequence.resize(200,200)

        self.write_sequence()

        self._main.gridlayout.addWidget(self.sequence_box,0,1,10,2)

        run_button = QtWidgets.QPushButton('Run Sequence', self._main)
        run_button.setToolTip("Run Sequence")
        self._main.gridlayout.addWidget(run_button,0,0,1,1)
        run_button.clicked.connect(self.start_sequence)

        stop_button = QtWidgets.QPushButton('Stop Sequence', self._main)
        stop_button.setToolTip("Stop Sequence immediately")
        self._main.gridlayout.addWidget(stop_button,1,0,1,1)
        stop_button.clicked.connect(self.stop_sequence)

        ##matplotlib integration from:
        ##https://matplotlib.org/gallery/user_interfaces/embedding_in_qt_sgskip.html#sphx-glr-gallery-user-interfaces-embedding-in-qt-sgskip-py
        plot_box = QtWidgets.QGroupBox(self._main)
        plot_box.gridlayout = QtWidgets.QGridLayout()
        self._main.gridlayout.addWidget(plot_box, 0,4, 5, 4)
        self.dynamic_canvas = FigureCanvas(Figure(figsize=(6, 5)))
#        self.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(self.dynamic_canvas,plot_box))
        plot_box.nav = NavigationToolbar(self.dynamic_canvas,plot_box)
        plot_box.gridlayout.addWidget(plot_box.nav,1,0,1,1)
        self._dynamic_ax1, self._dynamic_ax2 = self.dynamic_canvas.figure.subplots(2)
        plot_box.gridlayout.addWidget(self.dynamic_canvas,0,0,1,1)
        plot_box.setLayout(plot_box.gridlayout)

        self._main.setLayout(self._main.gridlayout)

    def initManualtab(self):

        self._manu.gridlayout = QtWidgets.QGridLayout()
        self._manu.setLayout(self._manu.gridlayout)
        measurebutton = QtWidgets.QPushButton('Start measurement', self)
        measurebutton.setToolTip("Start a measurement")
        self._manu.gridlayout.addWidget(measurebutton, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        measurebutton.clicked.connect(self.start_measure)
        #
        stopmeasurebutton = QtWidgets.QPushButton('Stop measurement', self)
        stopmeasurebutton.setToolTip("Stop a measurement")
        self._manu.gridlayout.addWidget(stopmeasurebutton, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        stopmeasurebutton.clicked.connect(self.stop_measure)
        #
        self.temptextbox = QtWidgets.QLineEdit(self)
        self.temptextbox.setText('20')
        self._manu.gridlayout.addWidget(self.temptextbox, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        tempbutton = QtWidgets.QPushButton('Set SR80 temperature', self)
        self._manu.gridlayout.addWidget(tempbutton, 1, 1, 1, 1, QtCore.Qt.AlignLeft)
        def set_temp():
            self.setsr80temp(float(self.temptextbox.text()))
        tempbutton.clicked.connect(set_temp)
        #

        reinitmotorbutton = QtWidgets.QPushButton('Reinit motor', self)
        reinitmotorbutton.setToolTip("Re-Initialize Mirror")
        self._manu.gridlayout.addWidget(reinitmotorbutton, 2, 0, 1, 1, QtCore.Qt.AlignLeft)
        reinitmotorbutton.clicked.connect(self.reinitmotor)
        #
        roofbutton = QtWidgets.QPushButton('Point to roof', self)
        roofbutton.setToolTip("Point mirror to roof")
        self._manu.gridlayout.addWidget(roofbutton, 3, 0, 1, 1, QtCore.Qt.AlignLeft)
        roofbutton.clicked.connect(self.motor.roof)
        #
        sr80button = QtWidgets.QPushButton('Point to SR80', self)
        sr80button.setToolTip("Point mirror to SR80 black body")
        self._manu.gridlayout.addWidget(sr80button, 4, 0, 1, 1, QtCore.Qt.AlignLeft)
        sr80button.clicked.connect(self.motor.blackbody)
        #
        parkbutton = QtWidgets.QPushButton('Park mirror', self)
        parkbutton.setToolTip("Point mirror to park position")
        self._manu.gridlayout.addWidget(parkbutton, 5, 0, 1, 1, QtCore.Qt.AlignLeft)
        parkbutton.clicked.connect(self.motor.park)
        #
        self.paramtextbox = QtWidgets.QLineEdit(self)
        self.paramtextbox.setText(' | '.join([k + ':' + str(j) for k, j in self.v80.meas_params.items()]))
        self._manu.gridlayout.addWidget(self.paramtextbox, 0, 3, 1, 4)
        parambutton = QtWidgets.QPushButton('Update params', self)
        parambutton.setToolTip("Set Vertex80 measurement parameters")
        self._manu.gridlayout.addWidget(parambutton, 1, 5, 1, 1, QtCore.Qt.AlignRight)
        parambutton.clicked.connect(self.setv80param)
        #
        # checkBox = QtWidgets.QCheckBox("checkbox")
        # if self.checkbox: checkBox.toggle()
        # checkBox.stateChanged.connect(self.setcheckbox)
        # self.gridlayout.addWidget(checkBox, 0, 1, 1 ,1, QtCore.Qt.AlignRight)
        #
        #
        # self.dirlistwidget = QtWidgets.QListWidget()
        # self.make_listwidget()
        ##import ipdb; ipdb.set_trace()
        # self.dirlistwidget.itemClicked.connect(self.listclick)
        # self.gridlayout.addWidget(self.dirlistwidget, 1,3,3,2, QtCore.Qt.AlignRight)
        #
        #        self.show_seq = QtWidgets.QTextEdit(self._main)
        #        self._main.gridlayout.addWidget(self.show_seq)
        # Status Box
        self.Init_StatusBox()
        #

    def initUI(self):
        self.main = QtWidgets.QWidget()

        self._tabs = QtWidgets.QTabWidget()
        self._main = QtWidgets.QWidget()
        self._manu = QtWidgets.QWidget()

        self.setCentralWidget(self.main)
        self.gridlayout = QtWidgets.QGridLayout()

        self._tabs.addTab(self._main,"Main")
        self._tabs.addTab(self._manu,"Manual")

        self.initMaintab()
        self.initManualtab()


        self.gridlayout.addWidget(self._tabs, 0, 0, 10, 1)
        self.main.setLayout(self.gridlayout)

        self._tabs.gridlayout = QtWidgets.QGridLayout()
        self._tabs.setLayout(self._tabs.gridlayout)

        self.gridlayout.setSpacing(10)


        self.setWindowTitle(self.title)
        left = 100
        top = 100
        width = 1000
        height = 800
        self.setGeometry(left,top,width,height)
        self.statusBar().showMessage('Loading')
        #
        mainMenu=self.menuBar()
        fileMenu=mainMenu.addMenu('File')
        #
        openButton = QtWidgets.QAction(QIcon('open24.png'), 'Open', self)
        openButton.setShortcut('Ctrl+O')
        openButton.setStatusTip('Open directory')
        openButton.triggered.connect(self.getfolder)
        fileMenu.addAction(openButton)
        #
        exitButton = QtWidgets.QAction(QIcon('exit24.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)
        #

        self.show()

    def Init_StatusBox(self):
        sbox = QtWidgets.QGroupBox(self.main)
        self.gridlayout.addWidget(sbox,0,1,10,1)

        sbox.gridlayout = QtWidgets.QGridLayout()
        title = QtWidgets.QLabel(sbox)
        title.setText('Status box')
        sbox.gridlayout.addWidget(title,0,0,1,1,QtCore.Qt.AlignLeft)

        tempbox = QtWidgets.QGroupBox(sbox)
        sbox.gridlayout(tempbox,0,0,1,1)

        tempbox.gridlayout = QtWidgets.QGridLayout()
        templabel = QtWidgets.QLabel(tempbox)
        templabel.setText('SR80 Temperature')
        sbox.gridlayout.addWidget(templabel,1,0,1,1,QtCore.Qt.AlignLeft)
#        self.sr80_temp = QtWidgets.QLabel(sbox)
#        sbox.gridlayout.addWidget(self.sr80_temp,1,1,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(sbox)
        sr80_l1.setText('Target')
        sbox.gridlayout.addWidget(sr80_l1, 1, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_target = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.sr80_target,1,2,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(sbox)
        sr80_l1.setText('Reached')
        sbox.gridlayout.addWidget(sr80_l1, 2, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_reached = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.sr80_reached,2,2,1,1,QtCore.Qt.AlignLeft)

        sr80_l1 = QtWidgets.QLabel(sbox)
        sr80_l1.setText('Stable')
        sbox.gridlayout.addWidget(sr80_l1, 3, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.sr80_status = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.sr80_status,3,2,1,1,QtCore.Qt.AlignLeft)


        ####

        v80_label = QtWidgets.QLabel(sbox)
        v80_label.setText('Vertex 80')
        sbox.gridlayout.addWidget(v80_label, 4, 0, 1, 1, QtCore.Qt.AlignLeft)

        v80_l1 = QtWidgets.QLabel(sbox)
        v80_l1.setText('Status')
        sbox.gridlayout.addWidget(v80_l1, 4, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_status = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.v80_status,4,2,1,1,QtCore.Qt.AlignLeft)

        v80_l4 = QtWidgets.QLabel(sbox)
        v80_l4.setText('Scans')
        sbox.gridlayout.addWidget(v80_l4, 5, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_scans = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.v80_scans,5,2,1,1,QtCore.Qt.AlignLeft)

        v80_l2 = QtWidgets.QLabel(sbox)
        v80_l2.setText('Detector')
        sbox.gridlayout.addWidget(v80_l2, 6, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_detector = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.v80_detector,6,2,1,1,QtCore.Qt.AlignLeft)

        v80_l3 = QtWidgets.QLabel(sbox)
        v80_l3.setText('Datafile')
        sbox.gridlayout.addWidget(v80_l3, 7, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.v80_datafile = QtWidgets.QLabel(sbox)
        sbox.gridlayout.addWidget(self.v80_datafile,7,2,1,1,QtCore.Qt.AlignLeft)

        sbox.setLayout(sbox.gridlayout)

    def Update_StatusBox(self):

        t = self.sr80.get_temperature()
        t1,t2,st = self.Temperature_reached()
        self.sr80_target.setText('%.2f'%self.bbtemp)
        self.sr80_reached.setText('%.2f'%t)
        self.sr80_status.setText('%s'%st)

        v80stat = self.v80.get_status()
        self.v80_status.setText(v80stat['status'])
        self.v80_detector.setText(v80stat['detector'])
        self.v80_datafile.setText(v80stat['datafile'])
        self.v80_scans.setText('%i/%i'%(v80stat['scans'],v80stat['restscans']))

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = nyaemgui() #NyaEM()
    sys.exit(app.exec_())
